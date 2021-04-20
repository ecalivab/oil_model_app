# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    type = models.CharField(max_length=1, blank=True, null=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Chokepoint(models.Model):
    chokepoint_id = models.IntegerField(primary_key=True)
    strait_name = models.CharField(max_length=50, blank=True, null=True)
    alpha = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'chokepoint'


class ChokepointRisk(models.Model):
    chokepoint_risk_id = models.IntegerField(primary_key=True)
    strait_name = models.CharField(max_length=50, blank=True, null=True)
    chokepoint_risk = models.FloatField(blank=True, null=True)
    year = models.CharField(max_length=4)

    class Meta:
        managed = False
        db_table = 'chokepoint_risk'


class CommodityLvh(models.Model):
    commodity_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    lvh = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'commodity_lvh'


class Corridor(models.Model):
    corridor_id = models.IntegerField(primary_key=True)
    corridor_name = models.CharField(unique=True, max_length=100, blank=True, null=True)
    load_country = models.CharField(max_length=20, blank=True, null=True)
    load_port = models.CharField(max_length=20, blank=True, null=True)
    discharge_port = models.CharField(max_length=20, blank=True, null=True)
    discharge_country = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'corridor'


class CorridorCk(models.Model):
    corridor_ck_id = models.IntegerField(primary_key=True)
    corridor = models.ForeignKey(Corridor, models.DO_NOTHING, blank=True, null=True)
    chokepoint = models.ForeignKey(Chokepoint, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'corridor_ck'


class CorridorFailure(models.Model):
    corridor_failure_id = models.IntegerField(primary_key=True)
    corridor = models.ForeignKey(Corridor, models.DO_NOTHING, blank=True, null=True)
    corridor_failure_captive = models.FloatField(blank=True, null=True)
    corridor_failure_no_captive = models.FloatField(blank=True, null=True)
    pipeline = models.ForeignKey('Pipeline', models.DO_NOTHING, blank=True, null=True)
    year = models.CharField(max_length=4)

    class Meta:
        managed = False
        db_table = 'corridor_failure'
        unique_together = (('corridor', 'pipeline', 'year'),)


class CorridorIntake(models.Model):
    corridor_intake_id = models.IntegerField(primary_key=True)
    corridor = models.ForeignKey(Corridor, models.DO_NOTHING, blank=True, null=True)
    commodity = models.ForeignKey(CommodityLvh, models.DO_NOTHING)
    intake = models.FloatField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'corridor_intake'


class CorridorPipeline(models.Model):
    corridor_pipeline_id = models.IntegerField(primary_key=True)
    corridor = models.ForeignKey(Corridor, models.DO_NOTHING, blank=True, null=True)
    pipeline = models.ForeignKey('Pipeline', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'corridor_pipeline'


class CorridorSeabranch(models.Model):
    corridor_seabranch_id = models.IntegerField(primary_key=True)
    corridor = models.ForeignKey(Corridor, models.DO_NOTHING, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    length = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'corridor_seabranch'


class CorridorWeight(models.Model):
    corridor_weight_id = models.IntegerField(primary_key=True)
    corridor_name = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    relative_weight = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'corridor_weight'


class CountryChokepoint(models.Model):
    country_ck_id = models.IntegerField(primary_key=True)
    chokepoint = models.ForeignKey(Chokepoint, models.DO_NOTHING)
    country = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'country_chokepoint'


class CountryPipeline(models.Model):
    country_pipeline_id = models.IntegerField(primary_key=True)
    pipeline = models.ForeignKey('Pipeline', models.DO_NOTHING)
    country = models.CharField(max_length=100, blank=True, null=True)
    length = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'country_pipeline'


class FinalRisk(models.Model):
    loadcountry = models.CharField(primary_key=True, max_length=10)
    averagefailure = models.CharField(max_length=10, blank=True, null=True)
    totalintake = models.CharField(max_length=10, blank=True, null=True)
    finalrisk = models.CharField(max_length=10, blank=True, null=True)
    commodity = models.CharField(max_length=10, blank=True, null=True)
    date = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'final_risk'


class GeoRisk(models.Model):
    country = models.CharField(primary_key=True, max_length=50)
    year = models.CharField(max_length=4)
    sea_risk = models.FloatField(blank=True, null=True)
    geo_risk = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'geo_risk'
        unique_together = (('country', 'year'),)


class Pipeline(models.Model):
    pipeline_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    total_length = models.FloatField(blank=True, null=True)
    share_val = models.FloatField(blank=True, null=True)
    load_port = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pipeline'


class PiracyIndex(models.Model):
    country = models.CharField(primary_key=True, max_length=50)
    year = models.CharField(max_length=4)
    piracy = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'piracy_index'
        unique_together = (('country', 'year'),)


class Wgi(models.Model):
    country = models.CharField(primary_key=True, max_length=50)
    year = models.CharField(max_length=4)
    voice_accountability = models.FloatField(blank=True, null=True)
    political_stability = models.FloatField(blank=True, null=True)
    gov_effectiviness = models.FloatField(blank=True, null=True)
    regulatory_quality = models.FloatField(blank=True, null=True)
    rule_of_law = models.FloatField(blank=True, null=True)
    control_of_corruption = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wgi'
        unique_together = (('country', 'year'),)
