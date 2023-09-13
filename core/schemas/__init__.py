from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Float, Text
from sqlalchemy.dialects.postgresql import JSONB
from core.connectors.postgre import db
from pgvector.sqlalchemy import Vector
from core.connectors.storage import storage_client


class BaseModel(db.Model):
    __abstract__ = True   # This ensures that the BaseModel isn't treated as a regular table/model.

    def save(self):
        db.session.add(self)
        db.session.commit()

# Only server owner


class User(BaseModel):
    __tablename__ = 'user'

    id = db.Column(String, primary_key=True, unique=True)

    # Meta
    status = db.Column(String, default='active', nullable=False)  # active, inactive
    date_created = db.Column(DateTime, default=datetime.utcnow)
    date_updated = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    email_id = db.Column(String, nullable=False)

    # Info
    name = db.Column(String)
    description = db.Column(Text)

    # Other
    @property
    def apikeys(self):
        return ApiKey.query.order_by(ApiKey.date_created.desc()).all()

    @property
    def segments(self):
        return Segment.query.order_by(Segment.date_created.desc()).limit(100).all()

    @property
    def devices(self):
        return Device.query.order_by(Device.date_created.desc()).all()

    def to_json(self, include_apikeys=False, include_segments=False, include_devices=False):
        result = {
            'id': self.id,

            # Meta
            'status': self.status,
            'date_created': self.date_created,
            'date_updated': self.date_updated,
            'email_id': self.email_id,

            # Info
            'name': self.name,
            'description': self.description
        }
        if include_apikeys:
            all_keys = self.apikeys
            result['apikeys'] = [key.to_json() for key in all_keys]
        if include_segments:
            latest_segments = self.segments
            result['segments'] = [item.to_json() for item in latest_segments]
        if include_devices:
            all_devices = self.devices
            result['devices'] = [item.to_json() for item in all_devices]
        return result


class ApiKey(BaseModel):
    __tablename__ = 'apikey'

    id = db.Column(String, primary_key=True, unique=True)

    # Meta
    date_created = db.Column(DateTime, default=datetime.utcnow)
    date_updated = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(String, default='active', nullable=False)  # active, inactive, deleted

    # Info
    access_level = db.Column(db.ARRAY(String))  # read, write, admin
    name = db.Column(String)
    description = db.Column(Text)
    key = db.Column(String, unique=True)

    def to_json(self):
        return {
            'id': self.id,

            # Meta
            'date_created': self.date_created,
            'date_updated': self.date_updated,
            'status': self.status,

            # Info
            'access_level': self.access_level,
            'name': self.name,
            'description': self.description,
            'key': self.key
        }


class Device(BaseModel):
    __tablename__ = 'device'

    id = db.Column(String, primary_key=True, unique=True)

    # Meta
    status = db.Column(String, default='active', nullable=False)  # active, inactive, deleted
    date_created = db.Column(DateTime, default=datetime.utcnow)
    date_updated = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Info
    name = db.Column(String)
    description = db.Column(Text)
    device_type = db.Column(String, default='desktop', nullable=False)  # desktop, mobile, tablet, etc.

    # Other
    segments = db.relationship('Segment', backref='device', order_by="desc(Segment.date_created)", lazy='dynamic')

    def to_json(self, include_segments=False):
        result = {
            'id': self.id,

            # Meta
            'status': self.status,
            'date_created': self.date_created,
            'date_updated': self.date_updated,

            # Info
            'name': self.name,
            'description': self.description,
            'device_type': self.device_type
        }
        if include_segments:
            # Limit segments to latest 100
            latest_segments = self.segments.limit(100).all()
            result['segments'] = [item.to_json() for item in latest_segments]

        return result


class Segment(BaseModel):
    __tablename__ = 'segment'

    id = db.Column(String, primary_key=True, unique=True)

    # Meta
    device_id = db.Column(String, ForeignKey('device.id'), index=True)

    status = db.Column(String, default='active', nullable=False)  # active, inactive, deleted
    item_type = db.Column(String, default='screenshot', nullable=False)  # screenshot, file, etc.
    date_created = db.Column(DateTime, default=datetime.utcnow)
    date_updated = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    date_generated = db.Column(DateTime, default=datetime.utcnow)
    available_in = db.Column(db.ARRAY(String))  # local, aws_s3, supabase, azure_blob etc.
    lat = db.Column(Float)
    lng = db.Column(Float)

    # Info
    vector = db.Column(Vector(768), nullable=False)
    name = db.Column(String)
    description = db.Column(Text)
    extracted_text = db.Column(Text)
    attributes = db.Column(JSONB)

    def to_json(self, get_vector=False, get_screenshot=False, get_bounding_box=False,
                get_page_html=False, include_fields=None):
        # Initialize an empty dictionary to hold the data
        data = {}

        # Initialize a dictionary for filtered attributes
        filtered_attributes = {}

        # Check if include_fields is None, if so, include all fields
        if include_fields is None:
            include_fields = [
                'id', 'user_id', 'device_id', 'status', 'item_type', 'date_created',
                'date_updated', 'date_generated', 'available_in', 'lat', 'lng',
                'name', 'description', 'extracted_text', 'attributes'
            ]

        for field in include_fields:
            if field.startswith('attributes.'):
                attr_key = field.split('.', 1)[1]
                filtered_attributes[attr_key] = self.attributes.get(attr_key, None)
                continue

            if hasattr(self, field):
                data[field] = getattr(self, field)

        if filtered_attributes:
            data['attributes'] = filtered_attributes

        if get_vector:
            data['vector'] = list(self.vector)

        if get_screenshot:
            data['screenshot_url'] = storage_client.get_file_url(f"segments/{self.id}/image.webp")

        if get_page_html:
            if self.attributes.get('page_html_available', False):
                data['page_html_url'] = storage_client.get_file_url(f"segments/{self.id}/page_html.html.lzma")
            else:
                data['page_html_url'] = None

        if get_bounding_box:
            if self.attributes.get('bounding_box_available', False):
                data['bounding_box_url'] = storage_client.get_file_url(
                    f"segments/{self.id}/bounding_box_data.json.lzma")
            else:
                data['bounding_box_url'] = None

        return data
