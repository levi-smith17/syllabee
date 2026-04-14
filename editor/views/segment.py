from ..forms import *
from .funcs import get_master_syllabus_and_segment_id, is_master_syllabus_archived, is_segment_archived, \
    is_segment_previously_published, replace_segment, verify_master_bond_course
from .mixins import MasterSyllabusLockedAccessMixin, MasterSyllabusTocContextMixin
from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import AccessMixin, PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, DetailView, TemplateView, UpdateView, View
from django.views.generic.base import ContextMixin


class SegmentAccessMixin(MasterSyllabusLockedAccessMixin, AccessMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if is_segment_archived(self.kwargs['pk']):
            self.type = 'archived'
            return self.handle_no_permission()
        elif is_segment_previously_published(self.kwargs['pk'], self.kwargs['master_syllabus_id']):
            self.type = 'locked'
            return self.handle_no_permission()
        else:
            return super(SegmentAccessMixin, self).dispatch(request, *args, **kwargs)

    def get_permission_denied_message(self):
        self.permission_denied_message = 'This segment is associated with a' + \
                                         ('n' if self.type == 'archived' else '') + ' ' + self.type + \
                                         ' master syllabus, so it cannot be deleted.'
        return self.permission_denied_message


class SegmentContextMixin(ContextMixin, View):
    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super(SegmentContextMixin, self).get_context_data(**kwargs)
        try:
            master_bond = MasterBond.objects.get(master_syllabus_id=self.kwargs['master_syllabus_id'],
                                                 segment=self.kwargs['pk'])
            self.object = Segment.objects.get(pk=self.kwargs['pk'])
            context = get_master_syllabus_and_segment_id(self.request, context, **self.kwargs)
        except (KeyError, MasterBond.DoesNotExist):
            self.object = (Segment.objects
                           .filter(masterbond__master_syllabus_id=self.kwargs['master_syllabus_id'])
                           .order_by('masterbond__order').first())
            context['master_syllabus'] = MasterSyllabus.objects.get(pk=self.kwargs['master_syllabus_id'])
            try:
                master_bond = MasterBond.objects.get(master_syllabus_id=self.kwargs['master_syllabus_id'],
                                                     segment=self.object)
            except MasterBond.DoesNotExist:
                master_bond = None
        context['segment'] = self.object
        if master_bond:
            context = get_master_syllabus_and_segment_id(self.request, context, **self.kwargs)
            segment_course_valid = verify_master_bond_course(master_bond)
            context['blocks'] = Block.objects.filter(bond__segment=self.object)
            context['bonds'] = Bond.objects.filter(segment=self.object)
            context['content_id'] = 'segment-' + str(self.object.id)
            context['invalid_segments'] = [] if segment_course_valid else [self.object.name]
            context['master_bond'] = master_bond
            context['master_syllabus_archived'] = is_master_syllabus_archived(self.kwargs['master_syllabus_id'])
            context['master_bonds_with_sections'] = MasterBond.objects.filter(Q(pk=master_bond.id) &
                                                                              ~Q(masterbondsection__section=None))
            context['segment'] = self.object
            context['segment_course_valid'] = segment_course_valid
            context['term'] = master_bond.master_syllabus.term
            context['title'] = str(self.object)
        return {**context, **environs}


class SegmentBatchView(PermissionRequiredMixin, MasterSyllabusLockedAccessMixin, MasterSyllabusTocContextMixin,
                       TemplateView):
    permission_required = ('editor.edit_segment',)
    template_name = 'editor/mastersyllabus/options/batch.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context['callback'] = 'done_close_full'
        context['master_syllabus'] = MasterSyllabus.objects.get(pk=self.kwargs['master_syllabus_id'])
        context['segments'] = (Segment.objects
                               .filter(owner=self.request.user,
                                       masterbond__master_syllabus=self.kwargs['master_syllabus_id'])
                               .order_by('masterbond__order')
                               .distinct())
        context['target'] = '#toc-container'
        self.request.session['toc_tab'] = 'segments'
        return {**context, **environs}


class SegmentCreateView(PermissionRequiredMixin, MasterSyllabusLockedAccessMixin, FormInvalidMixin,
                        MasterSyllabusTocContextMixin, CreateView):
    permission_required = ('editor.add_segment',)
    model = Segment
    form_class = SegmentForm
    template_name = 'core/offcanvas/add.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        object_id = form.save().id
        insert_order = self.kwargs['order'] + 10
        after_master_bonds = MasterBond.objects.filter(master_syllabus_id=self.kwargs['master_syllabus_id'],
                                                       order__gte=insert_order)
        increment_order = insert_order
        for after_master_bond in after_master_bonds:
            increment_order += 10
            after_master_bond.order = increment_order
            after_master_bond.save()
        master_bond = MasterBond(master_syllabus_id=self.kwargs['master_syllabus_id'], segment_id=object_id,
                                 order=insert_order, owner=self.request.user)
        master_bond.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['callback'] = 'done_load_content'
        context['content_id'] = 'segment-add'
        context['add_url'] = reverse('editor:mastersyllabus:segment:create', args=(self.kwargs['master_syllabus_id'],
                                                                   self.kwargs['order'],))
        context['target'] = '#toc-container'
        self.request.session['toc_tab'] = 'segments'
        return {**context, **environs}


class SegmentDeleteView(PermissionRequiredMixin, FormInvalidMixin, SegmentAccessMixin, MasterSyllabusTocContextMixin,
                        DeleteViewFormMixin, DeleteView):
    permission_required = ('editor.delete_segment',)
    model = Segment
    form_class = SegmentDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['callback'] = 'done_load_content'
        context['content_id'] = 'segment-' + str(self.object.id)
        context['modal']['target'] = '#toc-container'
        context['modal']['url'] = reverse('editor:mastersyllabus:segment:delete', args=(self.kwargs['master_syllabus_id'],
                                                                        self.object.id,))
        self.request.session['toc_tab'] = 'segments'
        return context


class SegmentDetailView(PermissionRequiredMixin, SegmentContextMixin, TemplateView):
    permission_required = ('editor.view_segment',)
    model = Segment
    template_name = 'editor/mastersyllabus/segment/card/card.html'


class SegmentDetailPreview(PermissionRequiredMixin, DetailView):
    permission_required = ('editor.change_segment', 'editor.delete_segment',)
    model = Segment
    template_name = 'editor/mastersyllabus/masterbond/segment.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        master_syllabus = MasterSyllabus.objects.get(pk=self.kwargs['master_syllabus_id'])
        context['block_only'] = False
        context['bonds'] = Bond.objects.filter(segment=self.object)
        context['master_syllabus'] = master_syllabus
        context['segment'] = Segment.objects.get(pk=self.kwargs['pk'])
        context['term'] = master_syllabus.term
        return {**context, **environs}


class SegmentUpdateView(PermissionRequiredMixin, MasterSyllabusLockedAccessMixin, FormInvalidMixin,
                        MasterSyllabusTocContextMixin, UpdateView):
    permission_required = ('editor.change_segment', 'editor.delete_segment',)
    model = Segment
    form_class = SegmentForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        if is_segment_archived(self.kwargs['pk']) or \
                is_segment_previously_published(self.kwargs['pk'], self.kwargs['master_syllabus_id']):
            context['callback'] = 'done_load_regions_replace'
        else:
            context['callback'] = 'done_load_content'
        context['content_id'] = 'segment-' + str(self.object.id)
        context['delete_url'] = reverse('editor:mastersyllabus:segment:delete', args=(self.kwargs['master_syllabus_id'], self.object.id,))
        context['edit_url'] = reverse('editor:mastersyllabus:segment:update', args=(self.kwargs['master_syllabus_id'], self.object.id,))
        context['next_url'] = self.request.GET.get('next')
        context['target'] = '#toc-container'
        self.request.session['toc_tab'] = 'segments'
        return {**context, **environs}

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.instance.owner = request.user
            if is_segment_archived(self.kwargs['pk']) or \
                    is_segment_previously_published(self.kwargs['pk'], self.kwargs['master_syllabus_id']):
                self.kwargs['pk'] = replace_segment(request, self.kwargs['master_syllabus_id'], self.kwargs['pk'])
            form.instance.id = self.kwargs['pk']
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
