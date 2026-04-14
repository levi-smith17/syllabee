from core.views.mixins import FormInvalidMixin
from django.views.generic import CreateView, UpdateView
from editor.views.block import BlockCreateMixin, BlockUpdateMixin
from editor.views.mixins import SectionRequiredAccessMixin
from editor.forms.blocks.schedule import *


class ScheduleBlockCreateView(SectionRequiredAccessMixin, BlockCreateMixin, FormInvalidMixin, CreateView):
    model = ScheduleBlock
    form_class = ScheduleBlockForm

    def form_valid(self, form):
        master_section = (MasterBondSection.objects
                          .filter(master_bond__master_syllabus_id=self.kwargs['master_syllabus_id'],
                                  master_bond__segment_id=self.kwargs['segment_id']).first())
        schedule = Schedule(course=master_section.section.course, term_length=master_section.section.term.length,
                            owner=self.request.user, effective_term=master_section.section.term)
        schedule.save()
        form.instance.schedule = schedule
        form.instance.full_screen = True
        form.instance.type = 'schedule'
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ScheduleBlockUpdateView(BlockUpdateMixin, FormInvalidMixin, UpdateView):
    model = ScheduleBlock
    form_class = ScheduleBlockForm
