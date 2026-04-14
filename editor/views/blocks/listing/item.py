from core.forms import ArrangeForm
from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, FormView, UpdateView, View
from django.views.generic.edit import FormMixin
from editor.forms.blocks.list_block import *


class ListBlockItemFormMixin(FormMixin, View):
    def get_success_url(self):
        return reverse('editor:block:list:update', args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                                        self.kwargs['block_id'],))


class ListBlockItemArrangeView(PermissionRequiredMixin, FormInvalidMixin, ListBlockItemFormMixin, FormView):
    form_class = ArrangeForm
    template_name = 'editor/helpers/modal/arrange.html'

    def form_valid(self, form):
        order = 9
        ordering = form.cleaned_data['ordering'].split('|')
        for item_id in ordering:
            item = ListBlockItem.objects.get(pk=item_id)
            item.order = order
            item.save()
            order += 9
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context['modal'] = {}
        context['modal']['items'] = (ListBlockItem.objects
                                     .filter(list_block_id=self.kwargs['block_id'])
                                     .values('id', name=models.F('content'))
                                     .order_by('order'))
        context['modal']['message'] = '<strong>NOTE</strong>: to rearrange the items on this list block, first ' \
                                      'select an item from the list below, then use the up and down arrow buttons ' \
                                      'to reorder the items, and then click the Save button to save your changes.'
        context['modal']['message_type'] = 'info'
        context['modal']['model'] = 'list items'
        context['modal']['target'] = '.offcanvas-full-container'
        context['modal']['url'] = reverse('editor:block:list:item:arrange',
                                          args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                                self.kwargs['block_id'],))
        return {**context, **environs}

    def has_permission(self):
        if self.request.user.has_perm('editor.change_listblockitem'):
            return True
        return False


class ListBlockItemCreateView(PermissionRequiredMixin, FormInvalidMixin, ListBlockItemFormMixin, CreateView):
    permission_required = 'editor.add_listblockitem'
    model = ListBlockItem
    form_class = ListBlockItemForm
    template_name = 'core/offcanvas/add.html'

    def form_valid(self, form):
        list_items = ListBlockItem.objects.filter(list_block_id=self.kwargs['block_id']).last()
        if list_items:
            form.instance.order = list_items.order + 9
        else:
            form.instance.order = 9
        form.instance.list_block = ListBlock.objects.get(pk=self.kwargs['block_id'])
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('editor:block:list:item:create', args=(self.kwargs['master_syllabus_id'],
                                                                           self.kwargs['segment_id'],
                                                                           self.kwargs['block_id'],))
        context['target'] = '.offcanvas-full-container'
        return {**context, **environs}

    def get_form_kwargs(self):
        kwargs = super(ListBlockItemCreateView, self).get_form_kwargs()
        kwargs.update({'block_id': self.kwargs['block_id']})
        kwargs.update({'user': self.request.user})
        return kwargs


class ListBlockItemDeleteView(PermissionRequiredMixin, FormInvalidMixin, DeleteViewFormMixin,
                              ListBlockItemFormMixin, DeleteView):
    permission_required = 'editor.delete_listblockitem'
    model = ListBlockItem
    form_class = ListBlockItemDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal']['target'] = '.offcanvas-full-container'
        context['modal']['url'] = reverse('editor:block:list:item:delete',
                                          args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                                self.kwargs['block_id'], self.object.id,))
        return context


class ListBlockItemUpdateView(PermissionRequiredMixin, FormInvalidMixin, ListBlockItemFormMixin, UpdateView):
    model = ListBlockItem
    form_class = ListBlockItemForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = reverse('editor:block:list:item:delete',
                                        args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                              self.kwargs['block_id'], self.object.id,))
        context['edit_url'] = reverse('editor:block:list:item:update',
                                      args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                            self.kwargs['block_id'], self.object.id))
        context['target'] = '.offcanvas-full-container'
        return {**context, **environs}

    def get_form_kwargs(self):
        kwargs = super(ListBlockItemUpdateView, self).get_form_kwargs()
        kwargs.update({'block_id': self.kwargs['block_id']})
        kwargs.update({'user': self.request.user})
        return kwargs

    def has_permission(self):
        if self.request.user.has_perm('editor.change_listblockitem') or \
                self.request.user.has_perm('editor.delete_listblockitem'):
            return True
        return False
