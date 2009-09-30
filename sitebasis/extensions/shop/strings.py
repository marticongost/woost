#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from cocktail.translations import translations

translations.define("Site.pricing_policies",
    ca = u"Polítiques de preus",
    es = u"Políticas de precios",
    en = u"Pricing policies"
)

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

translations.define("Product.price",
    ca = u"Preu",
    es = u"Precio",
    en = u"Price"
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
    en = u"Receiver"
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

# Pricing
#------------------------------------------------------------------------------
translations.define("Pricing",
    ca = u"Política de preus",
    es = u"Política de precios",
    en = u"Pricing policy"
)

translations.define("Pricing-plural",
    ca = u"Polítiques de preus",
    es = u"Políticas de precios",
    en = u"Pricing policies"
)

translations.define("Pricing.title",
    ca = u"Títol",
    es = u"Título",
    en = u"Title"
)

translations.define("Pricing.enabled",
    ca = u"Activa",
    es = u"Activa",
    en = u"Enabled"
)

translations.define("Pricing.start_date",
    ca = u"Data d'inici",
    es = u"Fecha de inicio",
    en = u"Start date"
)

translations.define("Pricing.end_date",
    ca = u"Data de fi",
    es = u"Fecha de fin",
    en = u"End date"
)

translations.define("Pricing.highlighted",
    ca = u"Destacada",
    es = u"Destacada",
    en = u"Highlighted"
)

# Order pricing
#------------------------------------------------------------------------------
translations.define("OrderPricing",
    ca = u"Política de preus de comanda",
    es = u"Política de precios de pedido",
    en = u"Order pricing policy"
)

translations.define("OrderPricing-plural",
    ca = u"Polítiques de preus de comanda",
    es = u"Políticas de precios de pedido",
    en = u"Order pricing policies"
)

translations.define("OrderPricing.matching_orders",
    ca = u"Comandes afectades",
    es = u"Pedidos afectados",
    en = u"Matching orders"
)

# Order price
#------------------------------------------------------------------------------
translations.define("OrderPrice",
    ca = u"Preu de comanda",
    es = u"Precio de pedido",
    en = u"Order price"
)

translations.define("OrderPrice-plural",
    ca = u"Preus de comanda",
    es = u"Precios de pedido",
    en = u"Order prices"
)

translations.define("OrderPrice.modifier",
    ca = u"Modificació",
    es = u"Modificación",
    en = u"Modifier"
)

translations.define("OrderPrice.modifier_type",
    ca = u"Tipus de modificació",
    es = u"Tipo de modificación",
    en = u"Modifier type"
)

# OrderShippingCost
#------------------------------------------------------------------------------
translations.define("OrderShippingCost",
    ca = u"Cost d'enviament de comanda",
    es = u"Coste de envío de pedido",
    en = u"Order shipping cost"
)

translations.define("OrderShippingCost-plural",
    ca = u"Costos d'enviament de comanda",
    es = u"Costes de envío de pedido",
    en = u"Order shipping costs"
)

translations.define("OrderShippingCost.modifier",
    ca = u"Modificació",
    es = u"Modificación",
    en = u"Modifier"
)

translations.define("OrderShippingCost.modifier_type",
    ca = u"Tipus de modificació",
    es = u"Tipo de modificación",
    en = u"Modifier type"
)

# OrderTax
#------------------------------------------------------------------------------
translations.define("OrderTax",
    ca = u"Impost sobre comanda",
    es = u"Impuesto sobre pedido",
    en = u"Order tax"
)

translations.define("OrderTax-plural",
    ca = u"Impostos sobre comandes",
    es = u"Impuestos sobre pedidos",
    en = u"Order taxes"
)

translations.define("OrderTax.tax_scope",
    ca = u"Àmbit de l'impost",
    es = u"Ámbito del impuesto",
    en = u"Tax scope"
)

translations.define("OrderTax.modifier",
    ca = u"Modificació",
    es = u"Modificación",
    en = u"Modifier"
)

translations.define("OrderTax.modifier_type",
    ca = u"Tipus de modificació",
    es = u"Tipo de modificación",
    en = u"Modifier type"
)

# EntryPricing
#------------------------------------------------------------------------------
translations.define("EntryPricing",
    ca = u"Política de preus de línia de comanda",
    es = u"Política de precios de linia de pedido",
    en = u"Order entry pricing policy"
)

translations.define("EntryPricing-plural",
    ca = u"Polítiques de preus de línia de comanda",
    es = u"Políticas de precios de linea de pedido",
    en = u"Order entry pricing policies"
)

translations.define("EntryPricing.matching_entries",
    ca = u"Línies de comanda afectades",
    es = u"Lineas de pedido afectadas",
    en = u"Matching order entries"
)

# ProductPrice
#------------------------------------------------------------------------------
translations.define("EntryPrice",
    ca = u"Preu de línia de comanda",
    es = u"Precio de linea de pedido",
    en = u"Order entry price"
)

translations.define("EntryPrice-plural",
    ca = u"Preus de línia de comanda",
    es = u"Precios de linea de pedido",
    en = u"Order entry prices"
)

translations.define("EntryPrice.modifier",
    ca = u"Modificació",
    es = u"Modificación",
    en = u"Modifier"
)

translations.define("EntryPrice.modifier_type",
    ca = u"Tipus de modificació",
    es = u"Tipo de modificación",
    en = u"Modifier type"
)

# EntrtyFreeUnits
#------------------------------------------------------------------------------
translations.define("EntryFreeUnits",
    ca = u"Unitats gratuïtes",
    es = u"Unidades gratuitas",
    en = u"Free units"
)

translations.define("EntryFreeUnits-plural",
    ca = u"Unitats gratuïtes",
    es = u"Unidades gratuitas",
    en = u"Free units"
)

translations.define("EntryFreeUnits.paid_units",
    ca = u"Unitats pagades",
    es = u"Unidades pagadas",
    en = u"Paid units"
)

translations.define("EntryFreeUnits.free_units",
    ca = u"Unitats de regal",
    es = u"Unidades de regalo",
    en = u"Free units"
)

translations.define("EntryFreeUnits.repeated",
    ca = u"Admet múltiples",
    es = u"Admite múltiples",
    en = u"Repeated"
)

# EntryShippingCost
#------------------------------------------------------------------------------
translations.define("EntryShippingCost",
    ca = u"Cost d'enviament de línia de comanda",
    es = u"Coste de envío de pedido",
    en = u"Order entry shipping cost"
)

translations.define("EntryShippingCost-plural",
    ca = u"Costos d'enviament de línia de comanda",
    es = u"Costes de envío de pedido",
    en = u"Order entry shipping costs"
)

translations.define("EntryShippingCost.modifier",
    ca = u"Modificació",
    es = u"Modificación",
    en = u"Modifier"
)

translations.define("EntryShippingCost.modifier_type",
    ca = u"Tipus de modificació",
    es = u"Tipo de modificación",
    en = u"Modifier type"
)

# EntryTax
#------------------------------------------------------------------------------
translations.define("EntryTax",
    ca = u"Impost sobre línia de comanda",
    es = u"Impuesto sobre linea de pedido",
    en = u"Order entry tax"
)

translations.define("EntryTax-plural",
    ca = u"Impostos sobre línia de comanda",
    es = u"Impuestos sobre linea de pedido",
    en = u"Order entry taxes"
)

translations.define("EntryTax.tax_scope",
    ca = u"Àmbit de l'impost",
    es = u"Ámbito del impuesto",
    en = u"Tax scope"
)

translations.define("EntryTax.modifier",
    ca = u"Modificació",
    es = u"Modificación",
    en = u"Modifier"
)

translations.define("EntryTax.modifier_type",
    ca = u"Tipus de modificació",
    es = u"Tipo de modificación",
    en = u"Modifier type"
)

# Modifier types
#------------------------------------------------------------------------------
translations.define("sitebasis.extensions.shop price_modifier_type absolute",
    ca = u"Absoluta",
    es = u"Absoluta",
    en = u"Absolute"
)

translations.define("sitebasis.extensions.shop price_modifier_type relative",
    ca = u"Relativa",
    es = u"Relativa",
    en = u"Relative"
)

translations.define("sitebasis.extensions.shop price_modifier_type percentage",
    ca = u"Percentual",
    es = u"Percentual",
    en = u"Percentage"
)

# Tax scopes
#------------------------------------------------------------------------------
translations.define("sitebasis.extensions.shop tax_scope price",
    ca = u"Preu",
    es = u"Precio",
    en = u"Price"
)

translations.define("sitebasis.extensions.shop tax_scope shipping",
    ca = u"Costos d'enviament",
    es = u"Costes de envío",
    en = u"Shipping"
)

translations.define("sitebasis.extensions.shop tax_scope total",
    ca = u"Total",
    es = u"Total",
    en = u"Total"
)


