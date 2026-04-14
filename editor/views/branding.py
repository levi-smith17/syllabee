from ..forms import *
from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView


class BrandingUpdateView(PermissionRequiredMixin, FormInvalidMixin, UpdateView):
    permission_required = ('editor.change_branding',)
    model = Branding
    form_class = BrandingForm
    success_url = reverse_lazy('core:index')
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['callback'] = 'done_generic'
        context['edit_message'] = {'alert_css': 'm-0', 'icon': '',
                                   'text': '<strong>NOTE</strong>: some settings require a page refresh to take '
                                           'effect.',
                                   'text_css': '', 'type': 'info'}
        context['edit_url'] = reverse('editor:branding:update', args=(1,))
        return {**context, **environs}
