# import datetime

# from django import forms
# from reserve_module.models import RoomBooking
#
#
# class CancelReserveForm(forms.ModelForm):
#     class Meta:
#         model = RoomBooking
#         fields = ['']
#         selected_roombooking = forms.ModelChoiceField(queryset=RoomBooking.objects.all(), label='انتخاب لیست رزرو',
#                                                       widget=forms.Select(attrs={'class': 'form-control'}))
#         confirm = forms.BooleanField(label='از حذف خود اطمینان دارم',
#                                      widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

#         def __init__(self, user_id, *args, **kwargs):
#             super(CancelReserveForm, self).__init__(*args, **kwargs)
#             self.fields['selected_roombooking'].queryset = RoomBooking.objects.filter(user_id=user_id,
#                                                                                       start_date__gt=datetime.date.today())
#             self.fields['selected_roombooking'].label_from_instance =
