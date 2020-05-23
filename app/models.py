from app import db


class Country(db.Model):
    __tablename__ = "country"
    ccode = db.Column(db.String(2), primary_key=True)
    country = db.Column(db.String(255), index=True)
    region = db.Column(db.String(255), index=True)


class Deployment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), index=True)
    cycles = db.relationship('Cycle', backref='deployment', lazy='dynamic')

    def __repr__(self):
        return f"<Deployment #{self.id}: {self.title}"


class Cycle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), index=True)
    # started = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean)
    deployment_id = db.Column(db.Integer, db.ForeignKey('deployment.id'))
    reports = db.relationship('Report', backref='cycle', lazy='dynamic')
    collections = db.relationship('Collection', backref='cycle', lazy='dynamic')


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    updated = db.Column(db.DateTime)
    cycle_id = db.Column(db.Integer, db.ForeignKey('cycle.id'))


class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, unique=True)
    ring = db.Column(db.Text)
    cycle_id = db.Column(db.Integer, db.ForeignKey('cycle.id'))

