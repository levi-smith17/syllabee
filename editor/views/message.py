from ..forms import MessageForm, MessageDeleteForm
from ..models import MasterSyllabus, Message
from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView, View
from django.views.generic.base import ContextMixin


class MessageSuccessURLContextMixin(ContextMixin, View):
    def get_success_url(self):
        try:
            return reverse('editor:mastersyllabus:toc_message', args=(self.kwargs['master_syllabus_id'],
                                                                     self.request.session.get('message_id')))
        except NoReverseMatch:
            return reverse('editor:mastersyllabus:toc', args=(self.kwargs['master_syllabus_id'],))


class MessageCreateView(PermissionRequiredMixin, FormInvalidMixin, MessageSuccessURLContextMixin, CreateView):
    permission_required = ('editor.add_message',)
    model = Message
    form_class = MessageForm
    template_name = 'core/offcanvas/add.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('editor:mastersyllabus:message:create', args=(self.kwargs['master_syllabus_id'],))
        context['callback'] = 'done_load_content'
        context['content_id'] = 'segment-add'
        context['target'] = '#toc-container'
        return {**context, **environs}

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageDeleteView(PermissionRequiredMixin, FormInvalidMixin, DeleteViewFormMixin, MessageSuccessURLContextMixin,
                        DeleteView):
    permission_required = ('editor.delete_message',)
    model = Message
    form_class = MessageDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['callback'] = 'done_load_content'
        context['content_id'] = 'message-' + str(self.object.id)
        context['modal']['target'] = '#toc-container'
        context['modal']['url'] = reverse('editor:mastersyllabus:message:delete',
                                          args=(self.kwargs['master_syllabus_id'], self.kwargs['pk'],))
        return context


class MessageDetailView(PermissionRequiredMixin, TemplateView):
    permission_required = ('editor.view_message',)
    model = Message
    template_name = 'editor/messages/card.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        if 'pk' in self.kwargs:
            message = Message.objects.get(pk=self.kwargs['pk'])
        else:
            try:
                message = Message.objects.filter(owner=self.request.user).first()
            except:
                message = None
        if message:
            context['content_id'] = 'message-' + str(message.id)
            self.request.session['message_id'] = message.id
        context['master_syllabus'] = MasterSyllabus.objects.get(pk=self.kwargs['master_syllabus_id'])
        context['message'] = message
        self.request.session['toc_tab'] = 'messages'
        return {**context, **environs}


class MessageUpdateView(PermissionRequiredMixin, FormInvalidMixin, MessageSuccessURLContextMixin, UpdateView):
    permission_required = ('editor.change_message',)
    model = Message
    form_class = MessageForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['callback'] = 'done_load_content'
        context['content_id'] = 'message-' + str(self.object.id)
        context['delete_url'] = None
        context['edit_url'] = reverse('editor:mastersyllabus:message:update', args=(self.kwargs['master_syllabus_id'],
                                                                                   self.object.id,))
        context['target'] = '#toc-container'
        return {**context, **environs}
