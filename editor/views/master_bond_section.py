from ..forms import *
from .mixins import MasterSyllabusLockedAccessMixin, MasterSyllabusTocContextMixin
from core.views.funcs import get_cbv_context, get_environs, get_lbv_context, handler_form, reset_pagination, \
    update_pagination
from core.views.mixins import FormInvalidMixin, ListViewContextMixin, SearchViewContextMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import IntegrityError
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, ListView, View
from django.views.generic.edit import FormMixin


class MasterBondSectionFilterFormMixin(FormMixin, View):
    def form_valid(self, form):
        course_prefixes = self.request.POST.getlist('course_prefixes', None)
        course_numbers = self.request.POST.getlist('course_numbers', None)
        course_names = self.request.POST.getlist('course_names', None)
        section_codes = self.request.POST.getlist('section_codes', None)
        terms = self.request.POST.getlist('terms', None)
        instructors = self.request.POST.getlist('instructors', None)
        formats = self.request.POST.getlist('formats', None)
        self.request.session['masterbondsection_filters'] = {}
        if course_prefixes:
            for i, course in enumerate(course_prefixes):
                self.request.session['masterbondsection_filters']['section__course__prefix__icontains-' +
                                                                  str(i)] = course
        if course_numbers:
            for i, course in enumerate(course_numbers):
                self.request.session['masterbondsection_filters']['section__course__number__icontains-' +
                                                                  str(i)] = course
        if course_names:
            for i, course in enumerate(course_names):
                self.request.session['masterbondsection_filters']['section__course__name__icontains-' +
                                                                  str(i)] = course
        if section_codes:
            for i, section_code in enumerate(section_codes):
                self.request.session['masterbondsection_filters']['section__section_code__icontains-' +
                                                                  str(i)] = section_code
        if terms:
            for i, term in enumerate(terms):
                self.request.session['masterbondsection_filters']['section__term__term_code__icontains-' +
                                                                  str(i)] = term
        if instructors:
            for i, instructor in enumerate(instructors):
                instructor = instructor.split(', ')
                self.request.session['masterbondsection_filters']['section__instructor__last_name__icontains-' +
                                                                  str(i)] = instructor[0]
                self.request.session['masterbondsection_filters']['section__instructor__first_name__icontains-' +
                                                                  str(i)] = instructor[1]
        if formats:
            for i, section_format in enumerate(formats):
                self.request.session['masterbondsection_filters']['section__format-' + str(i)] = section_format
        return super().form_valid(form)


class MasterBondSectionFilterView(PermissionRequiredMixin, FormInvalidMixin, MasterBondSectionFilterFormMixin,
                                  FormView):
    permission_required = ('editor.view_masterbondsection',)
    model = MasterBondSection
    form_class = MasterBondSectionFilterForm
    template_name = 'core/offcanvas/filter.html'
    success_url = reverse_lazy('editor:masterbond:sections')

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super(MasterBondSectionFilterView, self).get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context = get_lbv_context(self, context)
        context['filter_url'] = reverse('viewer:search:filter')
        context['target'] = '#for-syllabus-tab-pane'
        reset_pagination(self.request, context['model'], False, True)
        context = update_pagination(self, context)
        return {**context, **environs}


class MasterBondSectionListView(PermissionRequiredMixin, ListViewContextMixin, ListView):
    permission_required = ('editor.view_masterbondsection',)
    model = MasterBondSection


class MasterBondSectionSearchView(PermissionRequiredMixin, SearchViewContextMixin, ListView):
    permission_required = ('editor.view_masterbondsection',)
    model = MasterBondSection


class MasterBondSectionUpdateView(PermissionRequiredMixin, MasterSyllabusLockedAccessMixin, FormInvalidMixin,
                                  MasterSyllabusTocContextMixin, FormView):
    permission_required = ('editor.add_masterbondsection', 'editor.change_masterbondsection',
                           'editor.delete_masterbondsection',)
    form_class = MasterBondSectionsForm
    template_name = 'editor/mastersyllabus/masterbond/sections.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        master_syllabus = MasterSyllabus.objects.get(pk=self.kwargs['master_syllabus_id'])
        master_bond = MasterBond.objects.get(pk=self.kwargs['master_bond_id'])
        context['callback'] = 'done_load_content'
        context['content_id'] = 'segment-' + str(master_bond.segment.id)
        context['formset'] = self.form_class.sections(queryset=(MasterBondSection.objects
                                                                .filter(master_bond_id=self.kwargs['master_bond_id'])),
                                                      form_kwargs={'term_id': master_syllabus.term.id,
                                                                   'user': self.request.user}, )
        context['master_bond'] = master_bond
        context['master_syllabus_id'] = self.kwargs['master_syllabus_id']
        context['target'] = '#toc-container'
        return {**context, **environs}

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        master_syllabus = MasterSyllabus.objects.get(pk=self.kwargs['master_syllabus_id'])
        formset = form_class.sections(self.request.POST,
                                      queryset=(MasterBondSection.objects
                                                .filter(master_bond_id=self.kwargs['master_bond_id'])),
                                      form_kwargs={'term_id': master_syllabus.term.id, 'user': self.request.user})
        for form in formset:
            form.instance.master_bond_id = self.kwargs['master_bond_id']
            form.instance.owner = self.request.user
        form = self.get_form()
        if formset.is_valid():
            try:
                formset.save()
            except IntegrityError:
                return handler_form(self.request,
                                    exceptions={'exceptions': {'Sections can only be added once to each segment '
                                                               'association. Ensure that all sections selected are '
                                                               'unique.'}})
            return super().form_valid(form)
        return super().form_invalid(form)
