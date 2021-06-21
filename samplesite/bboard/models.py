from django.db import models
from django.db.utils import IntegrityError
from django.core import validators
from django.core.exceptions import ValidationError


# Create your models here.


class Bb(models.Model):
    title = models.CharField(max_length=50, verbose_name='Товар',
                             validators=[validators.MinLengthValidator(1, message='Very small length'),
                                         validators.MaxLengthValidator(51, message='Very big length')],
                             error_messages={'invalid': 'Неправильное название товара'})
    content = models.TextField(null=True, blank=True, verbose_name='Описание')
    price = models.FloatField(null=True, blank=True, verbose_name='Цена')
    published = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')
    rubric = models.ForeignKey('Rubric', null=True, on_delete=models.PROTECT, verbose_name='Рубрика')

    class Meta:
        verbose_name_plural = 'Объявления'
        verbose_name = 'Объявление'
        ordering = ['-published', 'title']

        # fields mast have unique value
        unique_together = (
            ('title', 'published'),
            ('title', 'price', 'rubric'),
             )

        # get latest version (get_early_by - early)
        get_latest_by = 'published'

        # create index with only product less 10000
        indexes = [
            models.Index(fields=['-published', 'title'],
                         name='bb_partial',
                         condition=models.Q(price__lte=10000))
        ]

        # create index with many fields
        index_together = [['published', 'title'],
                          ['title', 'price', 'rubric'],
                          ]

        try:
            constraints = (
                models.CheckConstraint(check=models.Q(price__gte=0) & models.Q(price__lte=60000000),
                                       name='bboard_rubric_price_constraint'),
            )
        except IntegrityError:
            print('Value Error')

    def clean(self):
        """Check content and price > 0"""
        errors = {}
        if not self.content:
            errors['content'] = ValidationError('Enter a description of the item being sold')

        if self.price and self.price < 0:
            errors['price'] = ValidationError('Specify a non-negative price value')

        if errors:
            raise ValidationError(errors)


class Rubric(models.Model):
    name = models.CharField(max_length=20, db_index=True, verbose_name='Название')

    def __str__(self):
        """For read in admin"""
        return self.name

    class Meta:
        verbose_name_plural = 'Рубрики'
        verbose_name = 'Рубрика'
        ordering = ['name']
