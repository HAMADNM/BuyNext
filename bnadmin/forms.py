from django import forms

from core.models import Category, SubCategory
from seller.models import Product

from .models import Offer
from .models import CategoryOfferBridge, ProductOfferBridge


class OfferForm(forms.ModelForm):
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.select_related("seller", "subcategory").order_by("name"),
        required=False,
        widget=forms.SelectMultiple(attrs={"size": 8}),
        help_text="Select one or more products for PRODUCT offers.",
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.order_by("name"),
        required=False,
        widget=forms.SelectMultiple(attrs={"size": 6}),
        help_text="Select one or more categories for CATEGORY offers.",
    )
    subcategories = forms.ModelMultipleChoiceField(
        queryset=SubCategory.objects.select_related("category").order_by("category__name", "name"),
        required=False,
        widget=forms.SelectMultiple(attrs={"size": 8}),
        help_text="Optional: select subcategories. Their parent categories are linked automatically.",
    )

    start_date = forms.DateTimeField(
        required=False,
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M",
            attrs={"type": "datetime-local"},
        ),
    )
    end_date = forms.DateTimeField(
        required=False,
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M",
            attrs={"type": "datetime-local"},
        ),
    )

    class Meta:
        model = Offer
        fields = [
            "title",
            "description",
            "offer_type",
            "banner_image",
            "redirect_url",
            "is_active",
            "start_date",
            "end_date",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].widget.attrs["rows"] = 3
        self.fields["is_active"].widget.attrs["class"] = "rounded border-slate-300"

        for field_name in [
            "title",
            "description",
            "offer_type",
            "banner_image",
            "redirect_url",
            "start_date",
            "end_date",
            "products",
            "categories",
            "subcategories",
        ]:
            widget = self.fields[field_name].widget
            current_classes = widget.attrs.get("class", "")
            widget.attrs["class"] = (
                f"{current_classes} w-full px-4 py-2.5 rounded-xl border border-slate-200 "
                "focus:border-primary focus:ring-primary/30"
            ).strip()

        if self.instance and self.instance.pk:
            selected_products = Product.objects.filter(
                product_offers__offer=self.instance
            )
            selected_categories = Category.objects.filter(
                category_offers__offer=self.instance
            )
            self.fields["products"].initial = selected_products
            self.fields["categories"].initial = selected_categories
            self.fields["subcategories"].initial = SubCategory.objects.filter(
                category__in=selected_categories
            )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        offer_type = cleaned_data.get("offer_type")
        products = cleaned_data.get("products")
        categories = cleaned_data.get("categories")
        subcategories = cleaned_data.get("subcategories")

        if start_date and end_date and end_date < start_date:
            self.add_error("end_date", "End date must be after start date.")

        if offer_type == "PRODUCT" and not products:
            self.add_error("products", "Select at least one product for Product Offer.")

        if offer_type == "CATEGORY" and not categories and not subcategories:
            self.add_error(
                "categories",
                "Select at least one category or subcategory for Category Offer.",
            )

        return cleaned_data

    def save(self, commit=True):
        offer = super().save(commit=commit)
        if not commit:
            return offer

        ProductOfferBridge.objects.filter(offer=offer).delete()
        CategoryOfferBridge.objects.filter(offer=offer).delete()

        offer_type = self.cleaned_data.get("offer_type")
        selected_products = self.cleaned_data.get("products")
        selected_categories = self.cleaned_data.get("categories")
        selected_subcategories = self.cleaned_data.get("subcategories")

        if offer_type == "PRODUCT":
            for product in selected_products:
                ProductOfferBridge.objects.get_or_create(offer=offer, product=product)
        elif offer_type == "CATEGORY":
            category_set = set(selected_categories)
            category_set.update(subcategory.category for subcategory in selected_subcategories)
            for category in category_set:
                CategoryOfferBridge.objects.get_or_create(offer=offer, category=category)

        return offer
