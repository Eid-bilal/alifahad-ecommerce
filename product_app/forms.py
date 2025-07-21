from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'description', 'category', 'offer_percentage', 'image_1', 'image_2', 'image_3']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter product description'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'offer_percentage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter discount offer', 'step': '0.01'}),
            'image_1': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'image_2': forms.ClearableFileInput(attrs={'class': 'form-control-file', 'required': False}),
            'image_3': forms.ClearableFileInput(attrs={'class': 'form-control-file', 'required': False}),
        }

    def clean_product_name(self):
        product_name = self.cleaned_data.get('product_name')
        # Exclude the current instance when editing (for uniqueness check)
        if Product.objects.exclude(id=self.instance.id).filter(product_name__iexact=product_name).exists():
            raise forms.ValidationError('A product with this name already exists.')
        return product_name.title()

    def clean_description(self):
        description = self.cleaned_data.get('description', '')
        if len(description) > 1000:
            raise forms.ValidationError('Description must be 100 characters or less.')
        return description

    def clean_offer_percentage(self):
        offer = self.cleaned_data.get('offer_percentage')
        if offer is not None and (offer < 0 or offer > 100):
            raise forms.ValidationError('Offer percentage must be between 0 and 100.')
        return offer

    def clean(self):
        cleaned_data = super().clean()
        for field in ['image_1', 'image_2', 'image_3']:
            image = cleaned_data.get(field)
            if image:
                # Check if the image is a new file upload (has 'name' attribute)
                if hasattr(image, 'name'):
                    if not image.name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        raise forms.ValidationError(f'Image {image.name} is not a valid format. Only jpg, jpeg, png, and webp are allowed.')
                # For existing Cloudinary images (CloudinaryResource), skip validation or check format if needed
                else:
                    # Optionally validate CloudinaryResource format if metadata is available
                    pass
        return cleaned_data