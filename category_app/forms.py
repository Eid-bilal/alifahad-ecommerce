from django import forms
from .models import Category
import re

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            'category_name',
            'category_image',
            'category_offer',
            'category_unit'
        ] 
        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
            'category_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'category_offer': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter category offer', 'step': '0.01'}),
            'category_unit': forms.Select(attrs={'class': 'form-control'}),  
        }

    def clean_category_name(self):
        category_name = self.cleaned_data.get('category_name')
        if Category.objects.filter(category_name__iexact=category_name).exists():
            raise forms.ValidationError('Category name already exists')

        if not re.match(r'^[A-Za-z ]*$', category_name):
            raise forms.ValidationError('Category name must contain only letters and spaces')
        return category_name
    
    def clean_category_image(self):
        image = self.cleaned_data.get('category_image')
        if image:
            if not image.name.endswith(('.png', '.jpeg', '.jpg', '.webp')):
                raise forms.ValidationError('Image must be in JPEG or PNG format.')
        return image

    def clean(self):
        cleaned_data = super().clean()
        category_name = cleaned_data.get('category_name')

        if category_name:
            cleaned_data['category_name'] = category_name.title()
        
        return cleaned_data
    



