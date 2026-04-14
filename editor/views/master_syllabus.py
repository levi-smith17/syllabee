from ..forms import *
from .funcs import (get_master_syllabus_and_segment_id, has_master_bonds, verify_master_syllabus_course,
                    verify_master_syllabus_content)
from .mixins import MasterSyllabusLockedAccessMixin
from core.views.funcs import (get_cbv_context, get_current_term, get_environs, get_loader_context, get_modal)
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import AccessMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView, View
from django.views.generic.base import ContextMixin
from viewer.models import SectionProgress


class MasterSyllabusAccessMixin(AccessMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if 'pk' in self.kwargs:  # We're attempting to publish a master segment.
            self.master_syllabus = MasterSyllabus.objects.get(id=self.kwargs['pk'])
            invalid_content = verify_master_syllabus_content(self.master_syllabus)
            invalid_courses = verify_master_syllabus_course(self.master_syllabus)
            #section_progress = SectionProgress.objects.filter(master_syllabus=self.master_syllabus)
            if self.master_syllabus.term.archived and self.master_syllabus.locked:
                self.permission_denied_message = 'This master syllabus cannot be unlocked as the term that it is ' \
                                                 'associated with is archived.'
                return self.handle_no_permission()
            elif self.master_syllabus.locked:
                pass
            elif not has_master_bonds(self.kwargs['pk']):
                self.permission_denied_message = 'This master syllabus cannot be locked as it must have at least one ' \
                                                 'segment associated with it.'
                return self.handle_no_permission()
            elif not invalid_courses[0]:
                self.permission_denied_message = 'This master syllabus cannot be locked as it contains at least one ' \
                                                 'invalid segment. Please review the following segment(s): <ul>'
                for segment in invalid_courses[1]:
                    self.permission_denied_message += '<li>' + segment + '</li>'
                self.permission_denied_message += '</ul>'
                return self.handle_no_permission()
            elif not invalid_content[0]:
                self.permission_denied_message = 'This master syllabus contains one or more segments that have no ' \
                                                 'content. Please review the following segment(s): <ul>'
                for segment in invalid_content[1]:
                    self.permission_denied_message += '<li>' + segment + '</li>'
                self.permission_denied_message += '</ul>'
                return self.handle_no_permission()
            elif self.master_syllabus.locked and not self.request.user.is_superuser:
                self.permission_denied_message = 'This master syllabus cannot be unlocked as the term that it is ' \
                                                 'associated with has already begun.'
                current_term = get_current_term()
                if self.master_syllabus.term.start_date <= current_term.start_date:
                    return self.handle_no_permission()
            elif self.master_syllabus.office_hours == '':
                self.permission_denied_message = 'Office hours for this master syllabus have not been set. This ' \
                                                 'master syllabus cannot be locked until office hours are defined.'
                return self.handle_no_permission()
        return super(MasterSyllabusAccessMixin, self).dispatch(request, *args, **kwargs)


class MasterSyllabusContextMixin(ContextMixin, View):
    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super(MasterSyllabusContextMixin, self).get_context_data(**kwargs)
        context = get_master_syllabus_and_segment_id(self.request, context, **self.kwargs)
        context['instructor'] = Profile.objects.get(pk=self.request.user.id)
        try:
            master_syllabus = self.object
        except AttributeError:
            master_syllabus = context['master_syllabus']
        context['master_syllabus'] = master_syllabus
        if master_syllabus:
            context['master_bonds'] = MasterBond.objects.filter(master_syllabus=master_syllabus, owner=self.request.user)
        return {**context, **environs}


class MasterSyllabusCreateView(PermissionRequiredMixin, FormInvalidMixin, CreateView):
    permission_required = ('editor.add_mastersyllabus',)
    model = MasterSyllabus
    form_class = MasterSyllabusCreateForm
    template_name = 'core/offcanvas/add.html'
    success_url = reverse_lazy('editor:mastersyllabus:list')

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('editor:mastersyllabus:create')
        context['callback'] = 'done_close_full'
        context['target'] = '#master-syllabi'
        return {**context, **environs}

    def get_form_kwargs(self):
        kwargs = super(MasterSyllabusCreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MasterSyllabusDeleteView(PermissionRequiredMixin, MasterSyllabusLockedAccessMixin, FormInvalidMixin,
                               DeleteViewFormMixin, DeleteView):
    permission_required = ('editor.delete_mastersyllabus',)
    model = MasterSyllabus
    form_class = MasterSyllabusDeleteForm
    raise_exception = True
    success_url = reverse_lazy('editor:mastersyllabus:list')

    def dispatch(self, request, *args, **kwargs):
        master_syllabus = MasterSyllabus.objects.get(pk=self.kwargs['pk'])
        section_progress = SectionProgress.objects.filter(master_syllabus=master_syllabus)
        if master_syllabus.interactive_view and section_progress.exists():
            self.permission_denied_message = ('At least one student has started the interactive syllabus activity. '
                                              'As a result, this master syllabus cannot be deleted.')
            return self.handle_no_permission()
        return super(MasterSyllabusDeleteView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['callback'] = 'done_load_search'
        context['modal']['target'] = '#master-syllabi'
        context['modal']['url'] = reverse('editor:mastersyllabus:delete', args=(self.kwargs['pk'],))
        return context

    def post(self, request, *args, **kwargs):
        if 'master_syllabus_id' in request.session:
            del request.session['master_syllabus_id']
        if 'segment_id' in request.session:
            del request.session['segment_id']
        if 'message_id' in request.session:
            del request.session['message_id']
        return super(MasterSyllabusDeleteView, self).post(request, *args, **kwargs)


class MasterSyllabusIndexView(PermissionRequiredMixin, MasterSyllabusContextMixin, TemplateView):
    permission_required = ('editor.view_mastersyllabus',)
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editable'] = True
        if 'master_syllabus_id' in self.request.session and 'segment_id' in self.request.session:
            content_toc_json = ('{"master_syllabus_id": "' + str(self.request.session.get('master_syllabus_id')) +
                                '", "segment_id": "' + str(self.request.session.get('segment_id')) + '"}')
        else:
            content_toc_json = '{"master_syllabus_id": "' + str(context['master_syllabus'].id) + '"}'
        profile_json = ('{"instructor_id": "' + str(context['instructor'].id) + '", "master_syllabus_id": "' +
                        str(context['master_syllabus'].id) + '"}')
        context.update(get_loader_context(content=content_toc_json, profile=profile_json, toc=content_toc_json,
                                          title=str(context['master_syllabus']), view='editor',
                                          url=reverse('editor:index')))
        return context


class MasterSyllabusInteractiveView(PermissionRequiredMixin, FormInvalidMixin, UpdateView):
    permission_required = ('editor.change_mastersyllabus',)
    model = MasterSyllabus
    form_class = MasterSyllabusInteractiveForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['callback'] = 'done_generic'
        context['delete_url'] = False
        context['edit_url'] = reverse('editor:mastersyllabus:interactive', args=(self.object.id,))
        context['target'] = '#toc-container'
        return {**context, **environs}

    def get_success_url(self):
        return reverse('editor:mastersyllabus:toc', args=(self.object.id,))


class MasterSyllabusListView(PermissionRequiredMixin, ListView):
    permission_required = ('editor.view_mastersyllabus',)
    model = MasterSyllabus
    template_name = 'editor/mastersyllabus/list.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['master_syllabi'] = MasterSyllabus.objects.filter(owner=self.request.user, term__archived=False)
        return {**context, **environs}


class MasterSyllabusLockView(PermissionRequiredMixin, MasterSyllabusAccessMixin, FormInvalidMixin, UpdateView):
    permission_required = ('editor.change_mastersyllabus',)
    model = MasterSyllabus
    form_class = MasterSyllabusLockForm
    template_name = 'editor/helpers/modal/generic.html'

    def form_valid(self, form):
        form.instance.locked = not bool(self.object.locked)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        message = '<strong>NOTE</strong>: '
        if self.object.locked:
            message += 'unlocking a master syllabus allows modifications to it and any associated segments and blocks.'
        else:
            message += 'locking a master syllabus prevents any modifications to it and any associated segments and ' \
                       'blocks.'
        context['callback'] = 'done_load_content'
        context['content_id'] = 'segment-' + str(self.request.session.get('segment_id'))
        context['modal'] = get_modal(message, message_alert_css='m-0', message_type='info',
                                     operation=('unlocked' if self.object.locked else 'locked'),
                                     target='#toc-container',
                                     submit_icon=('unlock' if self.object.locked else 'lock-fill'),
                                     submit_text=('Unlock' if self.object.locked else 'Lock'),
                                     url=reverse('editor:mastersyllabus:lock', args=(self.object.id,)))
        context['verbose_name'] = 'master syllabus'
        return {**context, **environs}

    def get_success_url(self):
        try:
            return reverse('editor:mastersyllabus:toc_segment', args=(self.object.id,
                                                                     self.request.session.get('segment_id')))
        except:
            return reverse('editor:mastersyllabus:toc', args=(self.object.id,))



class MasterSyllabusTocView(PermissionRequiredMixin, MasterSyllabusContextMixin, DetailView):
    permission_required = ('editor.view_mastersyllabus',)
    model = MasterSyllabus
    template_name = 'editor/mastersyllabus/toc.html'

    def dispatch(self, request, *args, **kwargs):
        if 'tab' in self.extra_context:
            self.request.session['toc_tab'] = self.extra_context['tab']
        return super(MasterSyllabusTocView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['grading_scales'] = GradingScale.objects.filter(owner=self.request.user)
        context['messages'] = Message.objects.filter(owner=self.request.user)
        return {**context, **environs}


class MasterSyllabusUpdateView(PermissionRequiredMixin, MasterSyllabusLockedAccessMixin, FormInvalidMixin, UpdateView):
    permission_required = ('editor.change_mastersyllabus',)
    model = MasterSyllabus
    form_class = MasterSyllabusUpdateForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['callback'] = 'done_load_regions'
        context['delete_url'] = False
        context['edit_url'] = reverse('editor:mastersyllabus:update', args=(self.object.id,))
        context['target'] = '#toc-container'
        return {**context, **environs}

    def get_success_url(self):
        try:
            return reverse('editor:mastersyllabus:toc_segment', args=(self.object.id,
                                                                     self.request.session.get('segment_id')))
        except:
            return reverse('editor:mastersyllabus:toc', args=(self.object.id,))
