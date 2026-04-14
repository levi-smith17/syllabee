import hashlib
from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin, FilterViewFormMixin, FormInvalidMixin, ListViewContextMixin, \
    SearchViewContextMixin
from django.contrib.auth.mixins import AccessMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, CreateView, DeleteView, ListView, UpdateView, View
from django.views.generic.edit import FormMixin
from editor.forms.registration.section import *


class SectionAccessMixin(AccessMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            archived = False
            if 'pk' in self.kwargs:  # We're attempting to edit or delete a section.
                archived = Section.objects.get(pk=self.kwargs['pk']).term.archived
            if archived:
                self.permission_denied_message = 'The term associated with this section has been archived, so this ' \
                                                 'section cannot be edited or deleted.'
                return self.handle_no_permission()
        return super(SectionAccessMixin, self).dispatch(request, *args, **kwargs)


class SectionFilterFormMixin(FormMixin, View):
    def form_valid(self, form):
        course_prefixes = self.request.POST.getlist('course_prefixes', None)
        course_numbers = self.request.POST.getlist('course_numbers', None)
        course_names = self.request.POST.getlist('course_names', None)
        section_codes = self.request.POST.getlist('section_codes', None)
        terms = self.request.POST.getlist('terms', None)
        instructors = self.request.POST.getlist('instructors', None)
        formats = self.request.POST.getlist('formats', None)
        self.request.session['section_filters'] = {}
        if course_prefixes:
            for i, course in enumerate(course_prefixes):
                self.request.session['section_filters']['course__prefix__icontains-' + str(i)] = course
        if course_numbers:
            for i, course in enumerate(course_numbers):
                self.request.session['section_filters']['course__number__icontains-' + str(i)] = course
        if course_names:
            for i, course in enumerate(course_names):
                self.request.session['section_filters']['course__name__icontains-' + str(i)] = course
        if section_codes:
            for i, section_code in enumerate(section_codes):
                self.request.session['section_filters']['section_code__icontains-' + str(i)] = section_code
        if terms:
            for i, term in enumerate(terms):
                self.request.session['section_filters']['term__term_code__icontains-' + str(i)] = term
        if instructors:
            for i, instructor in enumerate(instructors):
                instructor = instructor.split(', ')
                self.request.session['section_filters']['instructor__last_name__icontains-' + str(i)] = instructor[0]
                self.request.session['section_filters']['instructor__first_name__icontains-' + str(i)] = instructor[1]
        if formats:
            for i, section_format in enumerate(formats):
                self.request.session['section_filters']['format-' + str(i)] = section_format
        return super().form_valid(form)


class SectionCreateView(PermissionRequiredMixin, FormInvalidMixin, CreateView):
    permission_required = 'editor.add_section'
    model = Section
    form_class = SectionAddForm
    template_name = 'core/offcanvas/add.html'
    success_url = reverse_lazy('editor:registration:section:list')

    def form_valid(self, form):
        section = str(form.instance.course) + form.instance.section_code + str(form.instance.term)
        form.instance.hash = hashlib.md5(section.encode()).hexdigest()
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('editor:registration:section:create')
        context['target'] = '#content-container'
        return {**context, **environs}

    def get_form_kwargs(self):
        kwargs = super(SectionCreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class SectionDeleteView(PermissionRequiredMixin, SectionAccessMixin, FormInvalidMixin, DeleteViewFormMixin,
                        DeleteView):
    permission_required = 'editor.delete_section'
    model = Section
    form_class = SectionDeleteForm
    success_url = reverse_lazy('editor:registration:section:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal']['url'] = reverse('editor:registration:section:delete', args=(self.object.id,))
        return context


class SectionDetailView(PermissionRequiredMixin, ListViewContextMixin, ListView):
    permission_required = 'editor.view_section'
    model = Section

    def get_template_names(self):
        return ['editor/registration/card/card.html']


class SectionFilterView(PermissionRequiredMixin, FormInvalidMixin, FilterViewFormMixin, SectionFilterFormMixin,
                        FormView):
    permission_required = 'editor.view_section'
    model = Section
    form_class = SectionFilterForm
    template_name = 'core/offcanvas/filter.html'
    success_url = reverse_lazy('editor:registration:section:list')


class SectionListView(PermissionRequiredMixin, ListViewContextMixin, ListView):
    permission_required = 'editor.view_section'
    model = Section

    def get_template_names(self):
        return ['editor/registration/card/card.html']


class SectionSearchView(PermissionRequiredMixin, SearchViewContextMixin, ListView):
    permission_required = 'editor.view_section'
    model = Section

    def get_template_names(self):
        return ['editor/registration/card/card.html']


class SectionUpdateView(PermissionRequiredMixin, SectionAccessMixin, FormInvalidMixin, UpdateView):
    permission_required = ('editor.change_section', 'editor.delete_section',)
    model = Section
    form_class = SectionForm
    template_name = 'core/offcanvas/edit.html'
    success_url = reverse_lazy('editor:registration:section:list')

    def form_valid(self, form):
        section = str(form.instance.course) + form.instance.section_code + str(form.instance.term)
        form.instance.hash = hashlib.md5(section.encode()).hexdigest()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = None
        context['edit_url'] = reverse('editor:registration:section:update', args=(self.object.id,))
        if self.object.term.archived:
            context['change_perm'] = False
            context['delete_perm'] = False
        context['target'] = '#content-container'
        return {**context, **environs}

    def get_form_kwargs(self):
        kwargs = super(SectionUpdateView, self).get_form_kwargs()
        kwargs.update({'archived': self.object.term.archived})
        kwargs.update({'user': self.request.user})
        return kwargs
