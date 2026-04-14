from .mixins import InternshipDownloadPrintContextMixin
from ..forms import InternshipForm, InternshipDeleteForm
from ..models import Internship, InternshipLocation
from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group, User
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView, View
from django.views.generic.base import ContextMixin
from weasypdf.views import WeasypdfView


class InternshipContextMixin(ContextMixin, View):
    def get_success_url(self):
        if 'pk' in self.kwargs:
            return reverse('internship:journal:detail', args=(self.kwargs['pk'],))
        else:
            return reverse('internship:journal:detail')


class InternshipCreateView(PermissionRequiredMixin, FormInvalidMixin, InternshipContextMixin, CreateView):
    permission_required = ('internship.add_internship',)
    model = Internship
    form_class = InternshipForm
    template_name = 'core/offcanvas/add.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('internship:journal:create')
        context['callback'] = 'done_load_regions'
        context['target'] = '#content-container'
        return {**context, **environs}

    def get_form_kwargs(self):
        kwargs = super(InternshipCreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        user = User.objects.get(pk=self.object.intern.id)
        group = Group.objects.get(name='interns')
        # Add the student to the interns group
        if user and group:
            user.groups.add(group)
            user.save()
        return super().form_valid(form)


class InternshipDeleteView(PermissionRequiredMixin, FormInvalidMixin, DeleteViewFormMixin, DeleteView):
    permission_required = ('internship.delete_internship',)
    model = Internship
    form_class = InternshipDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['callback'] = 'done_load_regions'
        context['modal']['target'] = '#content-container'
        context['modal']['url'] = reverse('internship:journal:delete', args=(self.kwargs['pk'],))
        user = User.objects.get(pk=self.object.intern.id)
        group = Group.objects.get(name='interns')
        # Remove the student from the interns group
        if user and group:
            user.groups.remove(group)
            user.save()
        return context

    def get_success_url(self):
        return reverse('internship:journal:detail')


class InternshipDetailView(PermissionRequiredMixin, TemplateView):
    permission_required = ('internship.view_internship',)
    model = Internship
    template_name = 'internship/journal/card.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        if 'pk' in self.kwargs:
            try:
                internship = Internship.objects.get(pk=self.kwargs['pk'])
                self.request.session['internship_id'] = internship.id
            except Internship.DoesNotExist:
                internship = 0
        else:
            try:
                internship = Internship.objects.get(pk=self.request.session.get('internship_id'))
            except Internship.DoesNotExist:
                internship = 0
        context['internship'] = internship
        if internship:
            context['locations'] = InternshipLocation.objects.filter(internship=internship)
        return {**context, **environs}


class InternshipDownloadView(PermissionRequiredMixin, InternshipDownloadPrintContextMixin, WeasypdfView):
    permission_required = ('internship.view_internship',)
    body_template_name = 'internship/journal/print/index.html'
    header_template_name = ''
    footer_template_name = ''
    styles_template_name = 'weasypdf/print.scss'
    title = 'Internship Journal'


class InternshipPrintView(PermissionRequiredMixin, InternshipDownloadPrintContextMixin, TemplateView):
    permission_required = ('internship.view_internship',)
    template_name = 'internship/journal/print/index.html'


class InternshipUpdateView(PermissionRequiredMixin, FormInvalidMixin, InternshipContextMixin, UpdateView):
    permission_required = ('internship.change_internship',)
    model = Internship
    form_class = InternshipForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['callback'] = 'done_load_regions'
        context['delete_url'] = None
        context['edit_url'] = reverse('internship:journal:update', args=(self.object.id,))
        context['target'] = '#content-container'
        user = User.objects.get(pk=self.object.intern.id)
        group = Group.objects.get(name='interns')
        # Add the student to the interns group
        if user and group:
            user.groups.add(group)
            user.save()
        return {**context, **environs}

    def get_form_kwargs(self):
        kwargs = super(InternshipUpdateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs
