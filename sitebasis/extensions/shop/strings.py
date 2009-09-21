#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from cocktail.translations import translations

# Product
#------------------------------------------------------------------------------
translations.define("Product",
    ca = u"Producte",
    es = u"Producto",
    en = u"Product"
)

translations.define("Product-plural",
    ca = u"Productes",
    es = u"Productos",
    en = u"Products"
)

translations.define("Product.product_name",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("Product.price",
    ca = u"Preu",
    es = u"Precio",
    en = u"Price"
)

translations.define("Product.description",
    ca = u"Descripció",
    es = u"Descripción",
    en = u"Description"
)

translations.define("Product.categories",
    ca = u"Categories",
    es = u"Categorías",
    en = u"Categories"
)

# ProductCategory
#------------------------------------------------------------------------------
translations.define("ProductCategory",
    ca = u"Categoria de producte",
    es = u"Categoría de producto",
    en = u"Product category"
)

translations.define("ProductCategory-plural",
    ca = u"Categories de producte",
    es = u"Categorías de producto",
    en = u"Product categories"
)

translations.define("ProductCategory.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("ProductCategory.parent",
    ca = u"Categoria pare",
    es = u"Categoría padre",
    en = u"Parent category"
)

translations.define("ProductCategory.children",
    ca = u"Categories filles",
    es = u"Categorías hijas",
    en = u"Child categories"
)

translations.define("ProductCategory.products",
    ca = u"Productes",
    es = u"Productos",
    en = u"Products"
)

# ShopOrder
#------------------------------------------------------------------------------
translations.define("ShopOrder",
    ca = u"Comanda",
    es = u"Pedido",
    en = u"Shop order"
)

translations.define("ShopOrder-plural",
    ca = u"Comandes",
    es = u"Pedidos",
    en = u"Shop orders"
)

translations.define("ShopOrder.customer",
    ca = u"Client",
    es = u"Cliente",
    en = u"Client"
)

translations.define("ShopOrder.entries",
    ca = u"Contingut de la comanda",
    es = u"Contenido del pedido",
    en = u"Order entries"
)
    
translations.define("ShopOrder.shipping_address",
    ca = u"Adreça d'enviament",
    es = u"Dirección de envío",
    en = u"Shipping address"
)

translations.define("ShopOrder.cost",
    ca = u"Cost",
    es = u"Coste",
    en = u"Cost"
)

# ShippingAddress
#------------------------------------------------------------------------------
translations.define("ShippingAddress",
    ca = u"Adreça d'enviament",
    es = u"Dirección de envío",
    en = u"Shipping address"
)

translations.define("ShippingAddress-plural",
    ca = u"Adreces d'enviament",
    es = u"Direcciones de envío",
    en = u"Shipping addresses"
)

translations.define("ShippingAddress.receiver",
    ca = u"Destinatari",
    es = u"Destinatario",
    es = u"Receiver"
)       

translations.define("ShippingAddress.address",
    ca = u"Adreça",
    es = u"Dirección",
    en = u"Address"
)

translations.define("ShippingAddress.town",
    ca = u"Pobaclió",
    es = u"Población",
    en = u"Town"
)

translations.define("ShippingAddress.region",
    ca = u"Regió",
    es = u"Región",
    en = u"Region"
)

translations.define("ShippingAddress.country",
    ca = u"País",
    es = u"País",
    en = u"Country"
)

translations.define("ShippingAddress.postal_code",
    ca = u"Codi postal",
    es = u"Código postal",
    en = u"Postal code"
)

# Customer
#------------------------------------------------------------------------------
translations.define("Customer",
    ca = u"Client",
    es = u"Cliente",
    en = u"Customer"
)

translations.define("Customer-plural",
    ca = u"Clients",
    es = u"Clientes",
    en = u"Customers"
)

translations.define("Customer.first_name",
    ca = u"Nom",
    es = u"Nombre",
    en = u"First name"
)

translations.define("Customer.last_name",
    ca = u"Cognoms",
    es = u"Apellidos",
    en = u"Last name"
)

translations.define("Customer.phone_number",
    ca = u"Telèfon",
    es = u"Teléfono",
    en = u"Phone number"
)

translations.define("Customer.shop_orders",
    ca = u"Comandes",
    es = u"Pedidos",
    en = u"Shop orders"
)

# ShopOrderEntry
#------------------------------------------------------------------------------
translations.define("ShopOrderEntry",
    ca = u"Línia de comanda",
    es = u"Linea de pedido",
    en = u"Shop order entry"
)

translations.define("ShopOrderEntry-plural",
    ca = u"Línies de comanda",
    es = u"Lineas de pedido",
    en = u"Shop order entries"
)

translations.define("ShopOrderEntry.shop_order",
    ca = u"Comanda",
    es = u"Pedido",
    en = u"Shop order"
)

translations.define("ShopOrderEntry.product",
    ca = u"Producte",
    es = u"Producto",
    en = u"Product"
)

translations.define("ShopOrderEntry.quantity",
    ca = u"Quantitat",
    es = u"Cantidad",
    en = u"Quantity"
)

translations.define("ShopOrderEntry.product_price",
    ca = u"Preu del producte",
    es = u"Precio del producto",
    en = u"Product price"
)

