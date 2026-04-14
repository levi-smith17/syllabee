from ...forms import CourseForm, CourseCreateForm, CourseDeleteForm, CourseFilterForm, CourseRenameForm
from ...models import Course
from core.views.funcs import get_cbv_context, get_environs, handler_form
from core.views.mixins import DeleteViewFormMixin, FilterViewFormMixin, FormInvalidMixin, ListViewContextMixin, \
    SearchViewContextMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, CreateView, DeleteView, ListView, UpdateView


class CourseCreateView(PermissionRequiredMixin, FormInvalidMixin, CreateView):
    permission_required = 'editor.add_course'
    model = Course
    form_class = CourseCreateForm
    template_name = 'core/offcanvas/add.html'
    success_url = reverse_lazy('editor:registration:course:list')

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('editor:registration:course:create')
        context['target'] = '#content-container'
        return {**context, **environs}

    def form_valid(self, form):
        try:
            course = Course.objects.get(prefix=form.instance.prefix, number=form.instance.number, inactive=0,
                                        owner=self.request.user)
            if course:
                return handler_form(self.request,
                                    exceptions={
                                        'exceptions': {'You cannot add a duplicate course with the same prefix '
                                                       'and number that is active. If you are trying to replace a '
                                                       'course, then make the old course inactive first.'}})
        except Course.DoesNotExist:
            pass
        form.instance.course_code = form.instance.prefix + '-' + form.instance.number
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CourseDeleteView(PermissionRequiredMixin, FormInvalidMixin, DeleteViewFormMixin, DeleteView):
    permission_required = 'editor.delete_course'
    model = Course
    form_class = CourseDeleteForm
    success_url = reverse_lazy('editor:registration:course:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal']['url'] = reverse('editor:registration:course:delete', args=(self.object.id,))
        return context


class CourseDetailView(PermissionRequiredMixin, ListViewContextMixin, ListView):
    permission_required = 'editor.view_course'
    model = Course

    def get_template_names(self):
        return ['editor/registration/card/card.html']


class CourseFilterView(PermissionRequiredMixin, FormInvalidMixin, FilterViewFormMixin, FormView):
    permission_required = 'editor.view_course'
    model = Course
    form_class = CourseFilterForm
    template_name = 'core/offcanvas/filter.html'
    success_url = reverse_lazy('editor:registration:course:list')

    def form_valid(self, form):
        self.request.session['course_filters'] = {}
        course_prefixes = self.request.POST.getlist('course_prefixes', None)
        if course_prefixes:
            for i, course in enumerate(course_prefixes):
                self.request.session['course_filters']['prefix__icontains-' + str(i)] = course
        return super().form_valid(form)


class CourseListView(PermissionRequiredMixin, ListViewContextMixin, ListView):
    permission_required = 'editor.view_course'
    model = Course

    def get_template_names(self):
        return ['editor/registration/card/card.html']


class CourseRenameView(PermissionRequiredMixin, FormInvalidMixin, UpdateView):
    permission_required = ('editor.change_course',)
    model = Course
    form_class = CourseRenameForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = None
        context['edit_url'] = reverse('editor:registration:course:rename',
                                      args=(self.object.id, self.kwargs['program_id']))
        context['target'] = '#content-container'
        return {**context, **environs}

    def get_success_url(self):
        return reverse('curriculum:program:detail', args=(self.kwargs['program_id'],))


class CourseSearchView(PermissionRequiredMixin, SearchViewContextMixin, ListView):
    permission_required = 'editor.view_course'
    model = Course

    def get_template_names(self):
        return ['editor/registration/card/card.html']


class CourseUpdateView(PermissionRequiredMixin, FormInvalidMixin, UpdateView):
    permission_required = ('editor.change_course', 'editor.delete_course',)
    model = Course
    form_class = CourseForm
    template_name = 'core/offcanvas/edit.html'
    success_url = reverse_lazy('editor:registration:course:list')

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = None
        context['edit_url'] = reverse('editor:registration:course:update', args=(self.object.id,))
        context['target'] = '#content-container'
        return {**context, **environs}

    def form_valid(self, form):
        form.instance.code = form.instance.prefix + '-' + form.instance.number
        return super().form_valid(form)
