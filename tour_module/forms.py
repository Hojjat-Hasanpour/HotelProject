from datetime import date

from django import forms

from tour_module.models import TourBooking, Tour


class TourBookingModelForm(forms.ModelForm):
    class Meta:
        model = TourBooking
        fields = ['tour', 'number']

        widgets = {
            'tour': forms.Select(),
            'number': forms.NumberInput(attrs={'class': 'direction-rtl', 'placeholder': 'تعداد افراد را وارد نمایید'})
        }

        labels = {
            'tour': 'انتخاب تور',
            'number': 'تعداد افراد'
        }
        error_messages = {
            'tour': {
                'required': 'وارد کردن تور مورد نظر الزامی است.'
            },
            'number': {
                'required': 'وارد کردن تعداد افراد الزامی است.'
            }

        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(TourBookingModelForm, self).__init__(*args, **kwargs)
        TourBooking.objects.filter(user=user, is_paid=False, is_delete=False).delete()
        self.fields['tour'].queryset = Tour.objects.filter(is_active=True, start_date__gt=date.today()).exclude(
            tourbooking__user=user)

    def clean(self):
        super(TourBookingModelForm, self).clean()
        if self.cleaned_data.get('number') <= 0:
            self.add_error('number', 'عدد وارد شده نباید از 1 کوچکتر باشد.')


class CancelTourBookingModelForm(forms.ModelForm):
    confirm = forms.BooleanField(label='از حذف تور اطمینان دارم',
                                 widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = TourBooking
        fields = ['tour']
        # self.fields['tour'].queryset = TourBooking.objects.filter(user_id=self.request.user.id, is_delete=False)
        widgets = {
            'tour': forms.Select(),
        }
        labels = {
            'tour': 'انتخاب تور',
        }
        error_messages = {
            'tour': {
                'required': 'انتخاب تور مورد نظر الزامی است.'
            },
            'confirm': {
                'required': 'برای تایید لغو رزرواسیون این گزینه الزامی است.'
            }
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(CancelTourBookingModelForm, self).__init__(*args, **kwargs)
        self.fields['tour'].queryset = Tour.objects.filter(tourbooking__user=user, tourbooking__is_delete=False)

    # TourBooking.objects.filter(user=user, is_delete=False)
    # def __init__(self, *args, **kwargs):
    #     super(CancelTourBookingModelForm, self).__init__(*args, **kwargs)
    #     self.request = kwargs.pop("request")
    #     self.fields['tour'].queryset = TourBooking.objects.filter(user_id=self.request.user.id, is_delete=False)
