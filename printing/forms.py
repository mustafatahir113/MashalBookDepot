from django import forms

from .models import PrintingOrder


class PrintingOrderForm(forms.ModelForm):

    class Meta:
        model = PrintingOrder

        fields = [
            "description",
            "copies",
            "side",
            "print_type",
        ]

        widgets = {

            "description": forms.Textarea(
                attrs={
                    "class": "printing-input",
                    "placeholder": (
                        "Write Your Printing details here..."
                    ),
                    "rows": 5,
                }
            ),

            "copies": forms.NumberInput(
                attrs={
                    "class": "printing-input",
                    "min": 1,
                    "value": 1,
                }
            ),

            "side": forms.Select(
                attrs={
                    "class": "printing-input",
                }
            ),

            "print_type": forms.Select(
                attrs={
                    "class": "printing-input",
                }
            ),
        }

    def clean_copies(self):

        copies = self.cleaned_data.get("copies")

        if copies is None or copies < 1:
            raise forms.ValidationError(
                "Copies quantity kam az kam 1 honi chahiye."
            )

        return copies