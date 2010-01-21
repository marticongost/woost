#-*- coding: utf-8 -*-
<%inherit file="BaseView.mak"/>

<%!
from cocktail.translations import translations
from cocktail.html import templates
from woost.models import Site, Publishable, ModifyPermission

container_classes = "BaseView StandardView"
%>

<%def name="container()">

    <div class="header">
        ${self.header()}
    </div>

    ${self.menu()}

    <div class="main">
        ${self.main()}
    </div>

    <div class="footer">
        ${self.footer()}
    </div>

</%def>

<%def name="header()">    
    ${self.site_title()}
    ${self.identity()}
    ${self.language_selector()}
</%def>

<%def name="site_title()">
    <h1><a href="/">${Site.main.home.title}</a></h1>
</%def>

<%def name="language_selector()">
    ${self.create_language_selector().render()}
</%def>

<%def name="create_language_selector()">
    <%
    selector = templates.new("woost.views.LanguageSelector")
    selector.add_class("language_selector")
    return selector
    %>
</%def>

<%def name="identity()">
    % if user and not user.anonymous:
        <div class="identity">        
            <strong>${translations(user)}</strong>
            <form method="post">
                <button class="logout_button" name="logout" type="submit">
                    ${translations("Logout")}
                </button>
            </form>
        </div>
    % endif
</%def>

<%def name="create_menu()">
    <%
    menu = templates.new("woost.views.Menu")
    menu.add_class("menu")
    menu.root_visible = False
    menu.collapsible = True
    return menu
    %>
</%def>

<%def name="menu()">
    ${self.create_menu().render()}
</%def>

<%def name="publishable_title()">
    <h2>${publishable.inner_title or publishable.title}</h2>
</%def>

<%def name="toolbar()">
    % if user.has_permission(ModifyPermission, target = publishable):
        <div class="toolbar">
            <% backoffice = Publishable.get_instance(qname = "woost.backoffice") %>
            <a class="edit_link"
               href="${cms.uri(backoffice, 'content', publishable.id, 'fields')}">
                ${translations("Action edit")}
            </a>            
        </div>
    % endif
</%def>

<%def name="main()">
   
    ${self.publishable_title()}

    ${self.toolbar()}

    <div class="content">
        ${self.content()}
    </div>

    ${self.attachments()}
</%def>

<%def name="attachments()">
    <%
    attachments = [attachment
                   for attachment in publishable.attachments
                   if attachment.is_published()]
    %>
    % if attachments:
        <ul class="attachments">
            % for attachment in attachments:
                <li>
                    <a href="${cms.uri(attachment)}">
                        <img
                            src="${cms.icon_uri(attachment, icon_size = 16)}"
                            alt="${translations('woost.views.StandardView attachment icon description')}"/>
                        <span>${translations(attachment)}</span>
                    </a>
                </li>
            % endfor
        </ul>
    % endif
</%def>

<%def name="footer()">
</%def>

