import subprocess
import secrets
import argparse
import time


class DeploymentSetup:

    def __init__(self):
        self.color_codes = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "reset": "\033[0m"
        }

    def colored_print(self, text, color):
        print(self.color_codes[color] + text + self.color_codes["reset"])

    def prompt_for_env_var(self, prompt_text):
        return input(prompt_text + ": ").strip()

    def check_docker_installed(self):
        try:
            subprocess.run(["docker", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["docker-compose", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError:
            return False

    def modify_docker_compose_for_quickstart(self):
        with open('docker-compose.yml', 'r') as file:
            content = file.read()
            content = content.replace('build: .', 'image: infrhq/server:latest')

        with open('docker-compose.yml', 'w') as file:
            file.write(content)

    def revert_docker_compose(self):
        with open('docker-compose.yml', 'r') as file:
            content = file.read()
            content = content.replace('image: infrhq/server:latest', 'build: .')

        with open('docker-compose.yml', 'w') as file:
            file.write(content)

    def get_container_id_for_service(self, service_name):
        try:
            result = subprocess.run(["docker-compose", "ps", "-q", service_name], check=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.stdout.decode('utf-8').strip()
        except subprocess.CalledProcessError:
            self.colored_print(f"Failed to get container ID for service: {service_name}", "red")
            return None

    def listen_for_specific_log(self, key: str, timeout=60):
        start_time = time.time()
        container_id = self.get_container_id_for_service("web")
        if not container_id:
            self.colored_print("Failed to get container ID.", "red")
            return False

        while True:
            elapsed_time = time.time() - start_time

            if elapsed_time > timeout:
                self.colored_print("Timeout reached without finding the target log.", "yellow")
                break

            try:
                # Use subprocess to get the logs from the container using its ID
                result = subprocess.run(["docker", "logs", container_id, "--tail", "100"],
                                        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # Decode the logs and process line by line
                logs = result.stdout.decode('utf-8')
                for log_line in logs.splitlines():
                    if key in log_line:
                        self.colored_print(log_line, "green")
                        return True  # Exit the function once the log line is found

            except subprocess.CalledProcessError as e:
                self.colored_print(f"Failed to fetch logs! Reason: {e}", "red")
                break

            # Sleep for a while before checking the logs again
            time.sleep(5)  # checks every 5 seconds

        return False

    def deploy_with_docker(self, external_postgres, external_redis):
        self.colored_print("Starting deployment with Docker...", "blue")

        services_to_build_and_deploy = ["web"]
        if not external_postgres:
            services_to_build_and_deploy.append("db")
        if not external_redis:
            services_to_build_and_deploy.append("redis")

        try:
            # Building services
            subprocess.run(["docker-compose", "build"] + services_to_build_and_deploy, check=True)
            self.colored_print("Services built successfully!", "green")

            # Deploying services
            subprocess.run(["docker-compose", "up", "-d"] + services_to_build_and_deploy, check=True)
            self.colored_print("Application deployed successfully!", "green")

        except subprocess.CalledProcessError as e:
            self.colored_print(f"Deployment failed! Reason: {e}", "red")

    def setup_env_file(self):
        data = {
            "APP_SEC_DATA": self.get_app_sec_data(),
            "STORAGE_DATA": self.get_storage_data(),
            "SUPABASE_DATA": self.get_supabase_data(),
            **self.get_postgre_and_redis_data()
        }

        with open(".env", "w") as env_file:
            for key, value in data.items():
                if value:
                    env_file.write(f"{key}={value}\n")

        self.colored_print("\n.env file has been set up successfully!", "green")

    def get_app_sec_data(self):
        app_secret = self.prompt_for_env_var("Enter your APP Secret")
        admin_secret = self.prompt_for_env_var("Enter your Admin Secret")
        env_dev_prod = self.prompt_for_env_var("Enter your Environment (dev/prod)")
        host_url = self.prompt_for_env_var("Enter your Host URL")
        return f"{app_secret}|{admin_secret}|{env_dev_prod}|{host_url}"

    def get_storage_data(self):
        store_data_locally = input("Do you want to store data locally? (true/false): ").lower()
        if store_data_locally == "false":
            return f"{store_data_locally}|supabase"
        else:
            supabase_or_none = input("Do you want to use Supabase for storage as well? (supabase/none): ").lower()
            return f"{store_data_locally}|{supabase_or_none}"

    def get_supabase_data(self):
        supabase_option = self.prompt_for_env_var("Do you want to use Supabase for storage? (supabase/none)").lower()
        if supabase_option == "supabase":
            url_of_supabase = self.prompt_for_env_var("Enter your Supabase URL")
            api_key = self.prompt_for_env_var("Enter your Supabase API key")
            bucket = self.prompt_for_env_var("Enter your Supabase Bucket name")
            return f"{url_of_supabase}|{api_key}|{bucket}"
        return ""

    def get_postgre_and_redis_data(self):
        use_external_uri = input("Do you want to use external URIs for Postgres and Redis? (yes/no): ").lower()
        postgre_password = "password"
        if use_external_uri == "yes":
            POSTGRE_URI = self.prompt_for_env_var("Enter your Postgres URI")
            REDIS_URI = self.prompt_for_env_var("Enter your Redis URI")
        else:
            postgre_password = self.prompt_for_env_var("Enter your Postgres password")
            POSTGRE_URI = f"postgresql://postgres:{postgre_password}@db:5432/postgres"
            REDIS_URI = "redis://redis:6379/0"

        return {
            "POSTGRE_URI": POSTGRE_URI,
            "REDIS_URI": REDIS_URI,
            "FLASK_APP": "main.py",
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": postgre_password,
            "POSTGRES_DB": "postgres"
        }

    def quickstart_setup(self):
        self.colored_print("Running Quickstart Setup...", "blue")

        # Update compose to pull
        self.modify_docker_compose_for_quickstart()

        # Generating random secrets
        app_secret = secrets.token_urlsafe(16)
        admin_secret = secrets.token_urlsafe(16)
        env_dev_prod = "prod"
        host_url = "http://127.0.0.1:8000"
        postgres_password = secrets.token_urlsafe(16)

        # Setting values for .env file
        data = {
            "APP_SEC_DATA": f"{app_secret}|{admin_secret}|{env_dev_prod}|{host_url}",
            "STORAGE_DATA": "true|none",
            "POSTGRE_URI": f"postgresql://postgres:{postgres_password}@db:5432/postgres",
            "REDIS_URI": "redis://redis:6379/0",
            "FLASK_APP": "main.py",
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": postgres_password,
            "POSTGRES_DB": "postgres"
        }

        # Writing to .env file
        with open(".env", "w") as env_file:
            for key, value in data.items():
                env_file.write(f"{key}={value}\n")

        self.colored_print("\n.env file has been set up with default values! You can change them later.", "green")

        # Deploy using Docker
        self.deploy_with_docker(external_postgres=False, external_redis=False)

        self.colored_print(
            "Docker setup complete, files are being deployed. This process will wait for about 60 seconds.", "green")
        self.colored_print("Please don't close this window.", "yellow")
        time.sleep(60)
        self.listen_for_specific_log("Owner API key", timeout=60)
        self.colored_print(f"Head over to {host_url} & enter the API key for a simple Infr dashboard!", "green")
        self.revert_docker_compose()
        self.colored_print("\n\n======= Quickstart Setup Complete! =======\n\n", "green")

    def advanced_setup(self):

        skip_env_setup = input("Do you want to skip the .env setup? (yes/no): ").lower()
        deploy_postgre_and_redis = None

        if skip_env_setup != "yes":
            self.colored_print("Setting up .env file...", "blue")
            self.setup_env_file()
        else:
            self.colored_print("Skipping .env setup...", "yellow")

        if self.check_docker_installed():
            deploy_choice = input("Do you want to deploy the app using Docker now? (yes/no): ").lower()
            if deploy_choice == "yes":
                if deploy_postgre_and_redis is None:
                    deploy_postgre_and_redis = input(
                        "Do you want to deploy Postgres and Redis as well? (yes/no): ").lower() == "yes"
                self.deploy_with_docker(external_postgres=deploy_postgre_and_redis,
                                        external_redis=deploy_postgre_and_redis)
        else:
            self.colored_print(
                "Docker and/or Docker Compose are not installed. Please install them to deploy the app.", "red")

    def main(self, mode):
        self.colored_print("\n\n======= Deployment Setup for your Infr Server ⚡ =======\n\n", "green")

        if mode == "quickstart":
            self.quickstart_setup()
        elif mode == "advanced":
            self.advanced_setup()
        else:
            self.colored_print("Invalid option. Please choose either —quickstart or --advanced.", "red")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deployment Setup for your Infr Server")
    parser.add_argument('--advanced', action='store_true', help="Advanced setup mode")
    parser.add_argument('--quickstart', action='store_true', help="Quickstart setup mode")

    args = parser.parse_args()

    if args.advanced and args.quickstart:
        print("You can only choose one mode at a time: either --advanced or --quickstart")
        exit(1)
    elif args.advanced:
        mode = "advanced"
    elif args.quickstart:
        mode = "quickstart"
    else:
        mode = None

    setup = DeploymentSetup()
    setup.main(mode)
