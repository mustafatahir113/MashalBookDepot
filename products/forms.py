from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):

    rating = forms.ChoiceField(
        choices=[
            (1, '⭐ 1'),
            (2, '⭐⭐ 2'),
            (3, '⭐⭐⭐ 3'),
            (4, '⭐⭐⭐⭐ 4'),
            (5, '⭐⭐⭐⭐⭐ 5'),
        ],
        widget=forms.Select(
            attrs={
                'class': 'review-rating'
            }
        )
    )

    comment = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 5,
                'placeholder': (
                    'Write your review...'
                ),
                'class': 'review-comment-input'
            }
        )
    )

    class Meta:

        model = Review

        fields = [
            'rating',
            'comment'
        ]