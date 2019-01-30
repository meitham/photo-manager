# coding: utf-8
from sqlalchemy import (Boolean, CheckConstraint, Column, DateTime, Float,
                        ForeignKey, Integer, Numeric, SmallInteger, String,
                        Text, UniqueConstraint, text)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = Base.metadata


class PhotosCamera(Base):
    __tablename__ = 'photos_camera'

    id = Column(UUID, primary_key=True)
    created_at = Column(DateTime(True), nullable=False)
    updated_at = Column(DateTime(True), nullable=False)
    make = Column(String(128), nullable=False)
    model = Column(String(128), nullable=False)
    earliest_photo = Column(DateTime(True), nullable=False)
    latest_photo = Column(DateTime(True), nullable=False)


class PhotosLen(Base):
    __tablename__ = 'photos_lens'

    id = Column(UUID, primary_key=True)
    created_at = Column(DateTime(True), nullable=False)
    updated_at = Column(DateTime(True), nullable=False)
    name = Column(String(128), nullable=False)
    earliest_photo = Column(DateTime(True), nullable=False)
    latest_photo = Column(DateTime(True), nullable=False)


class PhotosTag(Base):
    __tablename__ = 'photos_tag'
    __table_args__ = (
        UniqueConstraint('name', 'type', 'source'),
    )

    id = Column(UUID, primary_key=True)
    created_at = Column(DateTime(True), nullable=False)
    updated_at = Column(DateTime(True), nullable=False)
    name = Column(String(128), nullable=False)
    type = Column(String(1))
    source = Column(String(1), nullable=False)
    parent_id = Column(ForeignKey('photos_tag.id', deferrable=True, initially='DEFERRED'), index=True)

    parent = relationship('PhotosTag', remote_side=[id])


class PhotosPhoto(Base):
    __tablename__ = 'photos_photo'
    __table_args__ = (
        CheckConstraint('classifier_color_version >= 0'),
        CheckConstraint('classifier_location_version >= 0'),
        CheckConstraint('classifier_object_version >= 0'),
        CheckConstraint('classifier_person_version >= 0'),
        CheckConstraint('classifier_style_version >= 0'),
        CheckConstraint('iso_speed >= 0'),
        CheckConstraint('last_thumbnailed_version >= 0')
    )

    id = Column(UUID, primary_key=True)
    created_at = Column(DateTime(True), nullable=False)
    updated_at = Column(DateTime(True), nullable=False)
    taken_at = Column(DateTime(True))
    taken_by = Column(String(128))
    aperture = Column(Numeric(3, 1))
    exposure = Column(String(8))
    iso_speed = Column(Integer)
    focal_length = Column(Numeric(4, 1))
    flash = Column(Boolean)
    metering_mode = Column(String(32))
    drive_mode = Column(String(32))
    shooting_mode = Column(String(32))
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    altitude = Column(Numeric(6, 1))
    last_thumbnailed_version = Column(Integer)
    last_thumbnailed_at = Column(DateTime(True))
    classifier_color_version = Column(Integer)
    classifier_color_queued_at = Column(DateTime(True))
    classifier_color_completed_at = Column(DateTime(True))
    classifier_location_version = Column(Integer)
    classifier_location_queued_at = Column(DateTime(True))
    classifier_location_completed_at = Column(DateTime(True))
    classifier_object_version = Column(Integer)
    classifier_object_queued_at = Column(DateTime(True))
    classifier_object_completed_at = Column(DateTime(True))
    classifier_person_version = Column(Integer)
    classifier_person_queued_at = Column(DateTime(True))
    classifier_person_completed_at = Column(DateTime(True))
    classifier_style_version = Column(Integer)
    classifier_style_queued_at = Column(DateTime(True))
    classifier_style_completed_at = Column(DateTime(True))
    camera_id = Column(ForeignKey('photos_camera.id', deferrable=True, initially='DEFERRED'), index=True)
    lens_id = Column(ForeignKey('photos_lens.id', deferrable=True, initially='DEFERRED'), index=True)

    camera = relationship('PhotosCamera')
    lens = relationship('PhotosLen')


class PhotosFace(Base):
    __tablename__ = 'photos_face'

    id = Column(UUID, primary_key=True)
    created_at = Column(DateTime(True), nullable=False)
    updated_at = Column(DateTime(True), nullable=False)
    position_x = Column(Float(53), nullable=False)
    position_y = Column(Float(53), nullable=False)
    size_x = Column(Float(53), nullable=False)
    size_y = Column(Float(53), nullable=False)
    source = Column(String(1), nullable=False)
    confidence = Column(Float(53), nullable=False)
    verified = Column(Boolean, nullable=False)
    hidden = Column(Boolean, nullable=False)
    photo_id = Column(ForeignKey('photos_photo.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    photo = relationship('PhotosPhoto')


class PhotosPhotofile(Base):
    __tablename__ = 'photos_photofile'
    __table_args__ = (
        CheckConstraint('bytes >= 0'),
        CheckConstraint('height >= 0'),
        CheckConstraint('width >= 0')
    )

    id = Column(UUID, primary_key=True)
    created_at = Column(DateTime(True), nullable=False)
    updated_at = Column(DateTime(True), nullable=False)
    path = Column(String(512), nullable=False)
    width = Column(SmallInteger, nullable=False)
    height = Column(SmallInteger, nullable=False)
    mimetype = Column(String(32), nullable=False)
    file_modified_at = Column(DateTime(True), nullable=False)
    bytes = Column(Integer, nullable=False)
    preferred = Column(Boolean, nullable=False)
    photo_id = Column(ForeignKey('photos_photo.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    photo = relationship('PhotosPhoto')


class PhotosPhototag(Base):
    __tablename__ = 'photos_phototag'
    __table_args__ = (
        CheckConstraint('model_version >= 0'),
    )

    id = Column(UUID, primary_key=True)
    created_at = Column(DateTime(True), nullable=False)
    updated_at = Column(DateTime(True), nullable=False)
    source = Column(String(1), nullable=False)
    model_version = Column(Integer)
    confidence = Column(Float(53), nullable=False)
    significance = Column(Float(53))
    verified = Column(Boolean, nullable=False)
    hidden = Column(Boolean, nullable=False)
    position_x = Column(Float(53))
    position_y = Column(Float(53))
    size_x = Column(Float(53))
    size_y = Column(Float(53))
    face_id = Column(ForeignKey('photos_face.id', deferrable=True, initially='DEFERRED'), index=True)
    photo_id = Column(ForeignKey('photos_photo.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    tag_id = Column(ForeignKey('photos_tag.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    face = relationship('PhotosFace')
    photo = relationship('PhotosPhoto')
    tag = relationship('PhotosTag')
