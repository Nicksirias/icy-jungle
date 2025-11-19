from django import forms


class EventForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        label="Event title",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Game night at the park"}),
    )
    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Share a few details about what to expect.",
            }
        ),
    )
    event_date = forms.DateTimeField(
        label="Event date & time",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        help_text="Use your local time zone.",
    )
    location = forms.CharField(
        max_length=255,
        label="Location",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Central Park, NYC"}),
    )

