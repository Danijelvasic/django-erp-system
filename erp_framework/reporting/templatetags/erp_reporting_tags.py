from __future__ import unicode_literals

from django import template
from django.template.defaultfilters import capfirst
from django.template.loader import get_template, render_to_string
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe

from erp_framework.base import app_settings

register = template.Library()


@register.simple_tag(takes_context=True)
def render_reports_menu(context, template_name="reporting/flat_menu.html", flat=True):
    request = context["request"]
    base_models = []
    reports = []

    from erp_framework.reporting.registry import report_registry

    if flat:
        reports = report_registry.get_all_reports()
    else:
        base_models = report_registry.get_base_models_with_reports()
    # if base_models:
    output = render_to_string(
        template_name,
        {
            "reports": reports,
            "base_models_reports_tuple": base_models,
            "is_report": context.get("is_report", False),
            "base_model": context.get("base_model", False),
            "report_slug": context.get("report_slug", False),
            "CURRENT_REPORT": context.get("CURRENT_REPORT", None),
            "current_base_model_name": context.get("current_base_model_name", False),
        },
        request,
    )
    return mark_safe(output)
    # return ""


@register.simple_tag(takes_context=True)
def is_active_report(
    context,
    report,
):
    current_report = context.get("CURRENT_REPORT", None)
    # breakpoint()
    if current_report:
        return current_report == report.__class__


@register.simple_tag(takes_context=True)
def get_report(context, base_model, report_slug):
    from erp_framework.reporting.registry import report_registry

    request = context["request"]
    try:
        current_app = request.current_app
    except AttributeError:
        current_app = app_settings.ERP_FRAMEWORK_SITE_NAME

    return report_registry.get(
        namespace=base_model, report_slug=report_slug, admin_site=current_app
    )


@register.simple_tag()
def get_model_verbose_name_plural(model):
    try:
        return capfirst(model._meta.verbose_name_plural)
    except:
        return "n/a"


@register.simple_tag(takes_context=True)
def get_report_active_class(context, base_model, css_class=None):
    css_class = css_class or "active"
    current_base_model_name = context["current_base_model_name"]
    return (
        css_class
        if current_base_model_name == base_model._meta.model_name.lower()
        else ""
    )


@register.simple_tag
def get_html_panel(report, template_name="", **kwargs):
    kwargs["report"] = report
    if not report:
        raise ValueError(
            "report argument is empty. Are you sure you're using the correct report name"
        )

    # No chart argument default to True if no charts in reports
    kwargs.setdefault("no_chart", not bool(report.chart_settings))
    kwargs.setdefault("data_display_chart_selector", kwargs["no_chart"])
    kwargs.setdefault("title", report.get_report_title())

    template = get_template(
        template_name or "erp_framework/report_widget_template.html"
    )
    return template.render(context=kwargs)


@register.simple_tag
def get_erp_settings():
    return app_settings.ERP_FRAMEWORK_SETTINGS
