
/*
    * Convert timestamp to readble date
    * GET Stats for segments
*/

function timeAgo(timestamp) {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  
    const date = new Date(timestamp);
    const now = new Date();
  
    const secondsPast = (now.getTime() - date.getTime()) / 1000;
  
    if (secondsPast < 60) {
      return `${parseInt(secondsPast)} seconds ago`;
    }
    if (secondsPast < 3600) {
      return `${parseInt(secondsPast / 60)} minutes ago`;
    }
    if (secondsPast <= 86400) {
      return `${parseInt(secondsPast / 3600)} hours ago`;
    }
    if (secondsPast <= 172800) { // 2 days
      return 'Yesterday';
    }
  
    const day = date.getDate();
    const monthIndex = date.getMonth();
    const year = date.getFullYear();
  
    return `${day} ${months[monthIndex]} ${year}`;
}
  

async function getSegmentStats() {

    var api_key = localStorage.getItem("apikey");
    if (!api_key) {
        return
    }

    try {
        let resp = await fetch("/v1/segment/query/stats", {
            method: "GET",
            headers: {
                "Infr-API-Key": api_key
            }
        });

        if (resp.ok) {
            let data = await resp.json();
            let stats = data.stats;

            let total_segments_stats = document.getElementById("segment__stat_total");
            total_segments_stats.innerHTML = stats.total_segments;

            let most_recent = document.getElementById("segment__stat_latest");
            most_recent.innerHTML = timeAgo(stats.last_segment.date_created);

            let latest_screenshot = document.getElementById("segment__stat_screenshot");
            latest_screenshot.innerHTML = (
                `<a href="${stats.last_segment.image_url}" class="btn btn-success" target="_blank">View</a>`
            )

            let seg_per_min = document.getElementById("segment__stat_segmin");
            let date = new Date(stats.first_segment.date_created);
            let now = new Date();
            let minutesPast = ((now.getTime() - date.getTime()) / 1000)/60;
            seg_per_min.innerHTML = (stats.total_segments/minutesPast).toFixed(2);
        }
    } catch (e) {
        console.log(e);
    }
}

getSegmentStats();

setInterval(getSegmentStats, 5000);
