# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.forms.models import inlineformset_factory
from django.template import loader
from django.contrib.contenttypes.models import ContentType
from basket.models import Order, BasketItem
from basket.utils import import_item, send_mail
from basket.settings import BASKET_FORM



class BaseOrderForm(forms.ModelForm):
    '''
    Order basket form. If you want to override default fields,
    set BASKET_FORM in settings.py. Fields will be merged with 
    this base form. For more information check default settings
    in basket/settings.py
    '''
    class Meta:
        model = Order
        exclude = ('user', 'session', 'status')


class ContactForm(forms.ModelForm):
    contact = forms.CharField(label=u'Ваш телефон', max_length=200)
    contact_time = forms.CharField(label=u'Удобное время для связи с вами',
        max_length=200, required=False)
    address = forms.CharField(label=u'Адрес для доставки', max_length=200)
    comment = forms.CharField(label=u'Комментарии', help_text='Поле не обязательное',
       max_length=200, required=False)

extend_form_class = import_item(BASKET_FORM, 'Can not import BASKET_FORM')


class OrderForm(extend_form_class, BaseOrderForm):
    pass

    def save(self, *args, **kwds):
        message = loader.render_to_string('basket/order.txt', {
            'order': self.instance,
            'data': self.cleaned_data,
        })
        send_mail(u'Форма заказа', message,
            [manager[1] for manager in settings.MANAGERS])


class BasketItemForm(forms.ModelForm):
    class Meta:
        model = BasketItem

    order = forms.CharField(max_length=100, widget=forms.HiddenInput)
    content_type = forms.ModelChoiceField(queryset=ContentType.objects.all(),
        widget=forms.HiddenInput)
    object_id = forms.IntegerField(widget=forms.HiddenInput)
    keep = forms.BooleanField(initial=True, required=False)

OrderFormset = inlineformset_factory(Order, BasketItem, extra=0, max_num=10,
    can_delete=False, form=BasketItemForm)
