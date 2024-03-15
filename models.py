from exts import db
from marshmallow import Schema, fields


class AirportModel(db.Model):
    __tablename__ = "airport"
    alias = db.Column(db.String(255), primary_key=True)
    wikidata = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(255), nullable=True)
    short = db.Column(db.String(255), nullable=False)
    iata = db.Column(db.String(3), nullable=True)
    icao = db.Column(db.String(4), nullable=True)
    lat = db.Column(db.Double, nullable=True)
    long = db.Column(db.Double, nullable=True)
    country = db.Column(db.String(255), nullable=True)


class AirportSchema(Schema):
    alias = fields.String()
    wikidata = fields.String()
    name = fields.String()
    short = fields.String()
    iata = fields.String()
    icao = fields.String()
    lat = fields.Float()
    long = fields.Float()
    country = fields.String()


class CountryModel(db.Model):
    __tablename__ = "country"
    wikidata = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
