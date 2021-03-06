from __future__ import unicode_literals

from django.db import models

from common.models import UUIDModel, VersionedModel


class Camera(UUIDModel, VersionedModel):
    make            = models.CharField(max_length=128)
    model           = models.CharField(max_length=128)
    earliest_photo  = models.DateTimeField()
    latest_photo    = models.DateTimeField()

    class Meta:
        ordering = ['make', 'model']

    def __str__(self):
        return '{} {}'.format(self.make, self.model)


class Lens(UUIDModel, VersionedModel):
    name            = models.CharField(max_length=128)
    earliest_photo  = models.DateTimeField()
    latest_photo    = models.DateTimeField()

    class Meta:
        verbose_name_plural = 'lenses'
        ordering = ['name']

    def __str__(self):
        return self.name


class Photo(UUIDModel, VersionedModel):
    taken_at                            = models.DateTimeField(null=True)
    taken_by                            = models.CharField(max_length=128, blank=True, null=True)
    aperture                            = models.DecimalField(max_digits=3, decimal_places=1, null=True)
    exposure                            = models.CharField(max_length=8, blank=True, null=True)
    iso_speed                           = models.PositiveIntegerField(null=True)
    focal_length                        = models.DecimalField(max_digits=4, decimal_places=1, null=True)
    flash                               = models.NullBooleanField()
    metering_mode                       = models.CharField(max_length=32, null=True)
    drive_mode                          = models.CharField(max_length=32, null=True)
    shooting_mode                       = models.CharField(max_length=32, null=True)
    camera                              = models.ForeignKey(Camera, related_name='photos', null=True, on_delete=models.CASCADE)
    lens                                = models.ForeignKey(Lens, related_name='photos', null=True, on_delete=models.CASCADE)
    latitude                            = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude                           = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    altitude                            = models.DecimalField(max_digits=6, decimal_places=1, null=True)
    last_thumbnailed_version            = models.PositiveIntegerField(null=True)
    last_thumbnailed_at                 = models.DateTimeField(null=True)
    classifier_color_version            = models.PositiveIntegerField(null=True)
    classifier_color_queued_at          = models.DateTimeField(null=True)
    classifier_color_completed_at       = models.DateTimeField(null=True)
    classifier_location_version         = models.PositiveIntegerField(null=True)
    classifier_location_queued_at       = models.DateTimeField(null=True)
    classifier_location_completed_at    = models.DateTimeField(null=True)
    classifier_object_version           = models.PositiveIntegerField(null=True)
    classifier_object_queued_at         = models.DateTimeField(null=True)
    classifier_object_completed_at      = models.DateTimeField(null=True)
    classifier_person_version           = models.PositiveIntegerField(null=True)
    classifier_person_queued_at         = models.DateTimeField(null=True)
    classifier_person_completed_at      = models.DateTimeField(null=True)
    classifier_style_version            = models.PositiveIntegerField(null=True)
    classifier_style_queued_at          = models.DateTimeField(null=True)
    classifier_style_completed_at       = models.DateTimeField(null=True)

    class Meta:
        ordering = ['-taken_at']

    def __str__(self):
        return str(self.id)

    # @property
    # def country(self):
    #     return country_from_point_field(self.location)

    def thumbnail_url(self, thumbnail):
        return '/thumbnails/{}x{}_{}_q{}/{}.jpg'.format(thumbnail[0], thumbnail[1], thumbnail[2], thumbnail[3], self.id)

    @property
    def file(self):
        return self.files.filter(mimetype='image/jpeg').order_by('preferred', '-created_at')[0]

    def clear_tags(self, source, type):
        self.photo_tags.filter(tag__source=source, tag__type=type).delete()

class PhotoFile(UUIDModel, VersionedModel):
    photo               = models.ForeignKey(Photo, related_name='files', on_delete=models.CASCADE)
    path                = models.CharField(max_length=512)
    width               = models.PositiveSmallIntegerField()
    height              = models.PositiveSmallIntegerField()
    mimetype            = models.CharField(max_length=32, blank=True)
    file_modified_at    = models.DateTimeField()
    bytes               = models.PositiveIntegerField()
    preferred           = models.BooleanField(default=False)

    def __str__(self):
        return str(self.path)

    @property
    def url(self):
        return self.path.split('/data', 1)[1]


SOURCE_CHOICES = (
    ('H', 'Human'),
    ('C', 'Computer'),
)
TAG_TYPE_CHOICES = (
    ('L', 'Location'),
    ('O', 'Object'),
    ('P', 'Person'),
    ('C', 'Color'),
    ('S', 'Style'),  # See Karayev et al.: Recognizing Image Style
)


class Face(UUIDModel, VersionedModel):
    photo       = models.ForeignKey(Photo, related_name='faces', on_delete=models.CASCADE)
    position_x  = models.FloatField()
    position_y  = models.FloatField()
    size_x      = models.FloatField()
    size_y      = models.FloatField()
    source      = models.CharField(max_length=1, choices=SOURCE_CHOICES)
    confidence  = models.FloatField()
    verified    = models.BooleanField(default=False)
    hidden      = models.BooleanField(default=False)


class Tag(UUIDModel, VersionedModel):
    name            = models.CharField(max_length=128)
    parent          = models.ForeignKey('Tag', related_name='+', null=True, on_delete=models.CASCADE)
    type            = models.CharField(max_length=1, choices=TAG_TYPE_CHOICES, null=True)
    source          = models.CharField(max_length=1, choices=SOURCE_CHOICES)

    class Meta:
        ordering = ['name']
        unique_together = (('name', 'type', 'source'),)

    def __str__(self):
        return '{} ({})'.format(self.name, self.type)


class PhotoTag(UUIDModel, VersionedModel):
    photo           = models.ForeignKey(Photo, related_name='photo_tags', on_delete=models.CASCADE)
    tag             = models.ForeignKey(Tag, related_name='photo_tags', on_delete=models.CASCADE)
    source          = models.CharField(max_length=1, choices=SOURCE_CHOICES)
    model_version   = models.PositiveIntegerField(null=True)
    confidence      = models.FloatField()
    significance    = models.FloatField(null=True)
    verified        = models.BooleanField(default=False)
    hidden          = models.BooleanField(default=False)
    # Only if the tag type is 'Person'
    face            = models.ForeignKey(Face, related_name='photo_tags', null=True, on_delete=models.CASCADE)
    # Optional bounding boxes from object detection
    position_x      = models.FloatField(null=True)
    position_y      = models.FloatField(null=True)
    size_x          = models.FloatField(null=True)
    size_y          = models.FloatField(null=True)

    class Meta:
        ordering = ['-significance']

    def __str__(self):
        return '{}: {}'.format(self.photo, self.tag)
