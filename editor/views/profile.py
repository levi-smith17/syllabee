from ..forms import ProfileForm
from ..models import Profile
from core.views.funcs import get_cbv_context, get_environs, get_office_hours
from core.views.mixins import FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, UpdateView


class ProfileDetailView(DetailView):
    model = Profile
    template_name = 'editor/profile/instructor.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        if 'master_syllabus_id' in self.kwargs:
            office_hours = get_office_hours(self.object.user, self.kwargs['master_syllabus_id'])
        elif 'master_syllabus_id' in self.request.session:
            office_hours = get_office_hours(self.object.user, self.request.session.get('master_syllabus_id'))
        else:
            office_hours = get_office_hours(self.object.user)
        context['instructor'] = self.object
        context['office_hours'] = office_hours
        context['print'] = False
        context['show_all'] = True
        return {**context, **environs}


class ProfileUpdateView(PermissionRequiredMixin, FormInvalidMixin, UpdateView):
    permission_required = ('editor.change_profile',)
    form_class = ProfileForm
    model = Profile
    template_name = 'core/offcanvas/edit.html'

    def form_valid(self, form):
        form.instance.username = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['edit_message'] = {'alert_css': 'm-0', 'icon': '',
                                   'text': '<strong>NOTE</strong>: changing your profile picture requires a page '
                                           'refresh to take effect.',
                                   'text_css': '', 'type': 'info'}
        context['edit_url'] = reverse('editor:profile:update', args=(self.object.id,))
        context['target'] = '#profile-container'
        return {**context, **environs}

    def get_form_kwargs(self):
        kwargs = super(ProfileUpdateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self):
        return reverse('editor:profile:detail', args=(self.object.id,))
