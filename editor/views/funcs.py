from ..models import *
from core.views.buttons import *
from core.views.funcs import get_current_term, handler400, handler403, handler404
from django.http import HttpResponseRedirect
from django.urls.exceptions import NoReverseMatch
from datetime import date, datetime


def batch_block_edit(request, master_syllabus_id, segment_id):
    """
    Batch edits all selected blocks based on the option selected (currently only unlinking is supported).

    Parameters:
    :param (object) request:                    The request object (for session variables).
    :param (int) master_syllabus_id:            The id of the master syllabus batch edit.
    :param (int) segment_id:                    The id of the segment to batch edit.

    Returns:
    :return (object)                            - Returns a request or an error object on failure.
    """
    if request.user.is_authenticated:
        if request.user.has_perm('editor.delete_bond'):
            if is_segment_archived(segment_id) or is_segment_previously_published(segment_id, master_syllabus_id):
                segment_id = replace_segment(request, master_syllabus_id, segment_id)
            try:
                batch_option = request.POST.get('batch_option')
                blocks_to_modify = request.POST.get('selected')
                blocks = blocks_to_modify.strip('|').split('|')
                if len(blocks_to_modify) > 0:
                    for block_id in blocks:
                        block = Bond.objects.get(segment_id=segment_id, block_id=block_id)
                        if batch_option == 'unlink':
                            block.delete()
                        else:
                            return handler403(request, 'Invalid option selected. Please try again.')
                else:
                    return handler403(request, 'No blocks selected!')
            except Exception as e:
                return handler400(request, str(e))
            return HttpResponseRedirect(reverse('editor:mastersyllabus:segment:detail', args=(master_syllabus_id, segment_id,)))
        else:
            return handler403(request)
    else:
        return handler404(request)


def batch_segment_edit(request, master_syllabus_id):
    """
        Modifies all selected segments based on the option selected.

        Parameters:
        :param (Request) request:                       The request object (for session variables).
        :param (MasterSyllabus) master_syllabus_id:     The id of the master syllabus to add segments to.

        Returns:
        :return (object)                                - Returns a request or an error object on failure.
        """
    if request.user.is_authenticated:
        if request.user.has_perm('editor.change_masterbond'):
            try:
                batch_option = request.POST.get('batch_option')
                segments_to_modify = request.POST.get('selected')
                segments = segments_to_modify.strip('|').split('|')
                if len(segments_to_modify) > 0:
                    for segment_id in segments:
                        segment = MasterBond.objects.get(master_syllabus_id=master_syllabus_id, segment_id=segment_id)
                        if batch_option == 'show':
                            segment.visibility = 1
                            segment.save()
                        elif batch_option == 'hide':
                            segment.visibility = 0
                            segment.save()
                        elif batch_option == 'unlink':
                            segment.delete()
                        else:
                            return handler403(request, 'Invalid option selected. Please try again.')
                else:
                    return handler403(request, 'No segments selected!')
            except Exception as e:
                return handler400(request, str(e))
            if 'segment_id' in request.session:
                return HttpResponseRedirect(reverse('editor:mastersyllabus:toc_segment',
                                                    args=(master_syllabus_id, request.session.get('segment_id'))))
            else:
                return HttpResponseRedirect(reverse('editor:mastersyllabus:toc', args=(master_syllabus_id,)))
        else:
            return handler403(request)
    else:
        return handler404(request)


def copy_bond_content(request, master_syllabus_id, segment_id):
    """
    Copies the requested blocks to a segment.

    Parameters:
    :param (object) request:                The request object (for session variables).
    :param (int) master_syllabus_id:        The id of the master syllabus to add blocks to.
    :param (int) segment_id:                The id of the segment to add blocks to.

    Returns:
    :return (object)                        - Returns a request or an error object on failure.
    """
    if request.user.is_authenticated:
        if request.user.has_perm('editor.add_bond') and \
                not (is_master_syllabus_archived(master_syllabus_id) or is_master_syllabus_locked(master_syllabus_id)):
            if is_segment_archived(segment_id) or is_segment_previously_published(segment_id, master_syllabus_id):
                segment_id = replace_segment(request, master_syllabus_id, segment_id)
            try:
                max_order = (Bond.objects.filter(segment_id=segment_id).order_by('-order').first())
                if max_order:
                    max_order = max_order.order
                else:
                    max_order = 0
                blocks_to_add = request.POST.get('selected')
                blocks = blocks_to_add.strip('|').split('|')
                if len(blocks_to_add) > 0:
                    for block in blocks:
                        max_order += 10
                        bond = Bond(segment_id=segment_id, block_id=int(block), order=max_order, owner=request.user)
                        bond.save()
                else:
                    return handler403(request, 'No blocks selected!')
            except Exception as e:
                return handler400(request, str(e))
            return HttpResponseRedirect(reverse('editor:mastersyllabus:segment:detail', args=(master_syllabus_id, segment_id,)))
        else:
            return handler403(request)
    else:
        return handler404(request)


def copy_masterbond_content(request, master_syllabus_id):
    """
    Copies the requested segments to a master syllabus.

    Parameters:
    :param (Request) request:                   The request object (for session variables).
    :param (int) master_syllabus_id:            The id of the master syllabus to add segments to.

    Returns:
    :return (object)                            - Returns a request or an error object on failure.
    """
    if request.user.is_authenticated:
        if request.user.has_perm('editor.add_masterbond') and \
                not (is_master_syllabus_archived(master_syllabus_id) or is_master_syllabus_locked(master_syllabus_id)):
            try:
                max_order = (MasterBond.objects
                             .filter(master_syllabus_id=master_syllabus_id)
                             .order_by('-order').first())
                if max_order:
                    max_order = max_order.order
                else:
                    max_order = 0
                segments_to_add = request.POST.get('selected')
                segments = segments_to_add.strip('|').split('|')
                if len(segments_to_add) > 0:
                    for segment in segments:
                        max_order += 10
                        master_bond = MasterBond(master_syllabus_id=master_syllabus_id, segment_id=int(segment),
                                                 order=max_order, owner=request.user, visibility=False)
                        master_bond.save()
                else:
                    return handler403(request, 'No segments selected!')
            except Exception as e:
                return handler400(request, str(e))
            try:
                return HttpResponseRedirect(reverse('editor:mastersyllabus:toc_segment',
                                                    args=(master_syllabus_id, request.session.get('segment_id'))))
            except NoReverseMatch:
                return HttpResponseRedirect(reverse('editor:mastersyllabus:toc', args=(master_syllabus_id,)))
        else:
            return handler403(request)
    else:
        return handler404(request)


def get_first_master_bond_segment_id(master_syllabus_id, segment_id=None):
    """
    Retrieves the first segment of a master bond of a master syllabus if one exists. None, otherwise.

    Parameters:
    :param (int) master_syllabus_id:    The master syllabus ID to retrieve a segment from.
    :param (int) segment_id:            The segment ID to check if exists.

    Returns:
    :return (int)                       - Returns a Segment ID if one exists. None, otherwise.
    """
    if segment_id:
        if MasterBond.objects.filter(master_syllabus_id=master_syllabus_id, segment_id=segment_id).exists():
            return segment_id
    first_master_bond = MasterBond.objects.filter(master_syllabus_id=master_syllabus_id).first()
    return first_master_bond.segment.id if first_master_bond else -1


def get_master_syllabus_and_segment_id(request, context, **kwargs):
    """
    Retrieves the proper master_syllabus_id and segment_id to autoload.

    Parameters:
    :param (Request) request:           The request object (for session variables).
    :param (dict) context:              The context to update with the proper autoload variables.

    Returns:
    :return (dict)                      - Returns a dictionary object representing a context.
    """
    if 'master_syllabus_id' in kwargs:
        context['master_syllabus'] = MasterSyllabus.objects.get(pk=kwargs['master_syllabus_id'])
    elif 'pk' in kwargs and 'master_syllabus_id' not in kwargs:
        context['master_syllabus'] = MasterSyllabus.objects.get(pk=kwargs['pk'])
        if 'segment_id' in request.session:
            del request.session['segment_id']
        if 'message_id' in request.session:
            del request.session['message_id']
    elif 'master_syllabus_id' in request.session:
        context['master_syllabus'] = MasterSyllabus.objects.get(pk=request.session.get('master_syllabus_id'))
    else:
        try:
            context['master_syllabus'] = MasterSyllabus.objects.get(term=get_current_term(), owner=request.user)
        except MasterSyllabus.DoesNotExist:
            context['master_syllabus'] = None
    request.session['master_syllabus_id'] = context['master_syllabus'].id if context['master_syllabus'] else None
    if 'toc_tab' in request.session:
        tab = request.session.get('toc_tab', 'segments')
    else:
        tab = 'segments'
    context['toc_tab'] = request.session['toc_tab'] = tab
    if tab == 'segments':
        if 'segment_id' in kwargs:
            context['segment_id'] = get_first_master_bond_segment_id(context['master_syllabus'].id, kwargs['segment_id'])
        elif 'pk' in kwargs and 'master_syllabus_id' in kwargs and 'segment_id' not in kwargs:
            context['segment_id'] = kwargs['pk']
            context['segment_id'] = get_first_master_bond_segment_id(context['master_syllabus'].id, kwargs['pk'])
        elif 'segment_id' in request.session:
            context['segment_id'] = get_first_master_bond_segment_id(request.session.get('master_syllabus_id'),
                                                                     request.session.get('segment_id'))
        else:
            context['segment_id'] = get_first_master_bond_segment_id(context['master_syllabus'].id)
        request.session['segment_id'] = context['segment_id']
        if 'message_id' in request.session:
            del request.session['message_id']
        context['message_id'] = -1
    else:
        if 'message_id' in kwargs:
            context['message_id'] = request.session['message_id'] = kwargs['message_id']
        elif 'message_id' in request.session:
            context['message_id'] = request.session.get('message_id')
        else:
            first_message = Message.objects.filter(owner=request.user).first()
            context['message_id'] = request.session['message_id'] = first_message.id if first_message else -1
        if 'segment_id' in request.session:
            del request.session['segment_id']
        context['segment_id'] = -1
    return context


def has_master_bonds(master_syllabus_id):
    """
    Determines whether a master syllabus has any MasterBonds associated with it or not.

    Parameters:
    :param (int) master_syllabus_id:    The master syllabus ID to check.

    Returns:
    :return (boolean)                   - Returns True if this master syllabus has MasterBonds. False, otherwise.
    """
    return MasterBond.objects.filter(master_syllabus_id=master_syllabus_id).exists()


def is_addendum_necessary(master_syllabus_id, segment_id, block_id):
    """
    Determines whether an addendum is necessary for the given master syllabus, segment, and block IDs.

    Parameters:
    :param (int) master_syllabus_id:    The id of the master syllabus to check.
    :param (int) segment_id:            The id of the segment to check.
    :param (int) block_id:              The id of the block to check.

    Returns:
    :return (boolean)                   - Returns True if an addendum is necessary. False, otherwise.
    """
    if is_block_archived(block_id) or is_block_previously_published(block_id, master_syllabus_id):
        # If either of these conditions are true, then an addendum is automatically necessary.
        return True
    else:
        # The block is not archived or previously published, so verify that it's not associated with an active term.
        master_syllabus = MasterSyllabus.objects.get(pk=master_syllabus_id)
        master_bond = MasterBond.objects.get(master_syllabus=master_syllabus, segment_id=segment_id)
        master_bond_sections = MasterBondSection.objects.filter(master_bond_id=master_bond)
        addendum_necessary = False
        if master_bond_sections:
            # The segment has section associations, so check against the section term start date(s).
            for master_bond_section in master_bond_sections:
                if date.today() > master_bond_section.section.term.start_date:
                    addendum_necessary = True
                    break
        else:
            # The segment is associated with all sections, so check against the term start date.
            if date.today() > master_syllabus.term.start_date:
                addendum_necessary = True
    return addendum_necessary


def is_block_archived(block_id):
    """
    Determines whether a block is associated with any segment that's archived or not.

    Parameters:
    :param (int) block_id:      The id of the block to check.

    Returns:
    :return (boolean)           - Returns True if this block is archived. False, otherwise.
    """
    return Bond.objects.filter(block_id=block_id, segment__masterbond__master_syllabus__term__archived=True).exists()


def is_block_previously_published(block_id, master_syllabus_id):
    """
    Determines whether a block is associated with any segment that's published or not.

    Parameters:
    :param (int) block_id:              The id of the block to check.
    :param (int) master_syllabus_id:    The master syllabus ID to check.

    Returns:
    :return (boolean)                   - Returns True if this block was previously published. False, otherwise.
    """
    return Bond.objects.filter(Q(block_id=block_id) & Q(segment__masterbond__visibility=True) &
                               ~Q(segment__masterbond__master_syllabus_id=master_syllabus_id)).exists()


def is_master_syllabus_archived(master_syllabus_id):
    """
    Determines whether a master syllabus is archived or not.

    Parameters:
    :param (int) master_syllabus_id:    The master syllabus ID to check.

    Returns:
    :return (boolean)                   - Returns True if this master syllabus is archived. False, otherwise.
    """
    return MasterSyllabus.objects.get(pk=master_syllabus_id).term.archived


def is_master_syllabus_locked(master_syllabus_id):
    """
    Determines whether a master syllabus is locked or not.

    Parameters:
    :param (int) master_syllabus_id:    The master syllabus ID to check.

    Returns:
    :return (boolean)                   - Returns True if this master syllabus is locked. False, otherwise.
    """
    return MasterSyllabus.objects.get(pk=master_syllabus_id).locked


def is_segment_archived(segment_id):
    """
    Determines whether a segment is associated with any master syllabus that's archived or not.

    Parameters:
    :param (int) segment_id:        The segment ID to check.

    Returns:
    :return (boolean)               - Returns True if this segment is archived. False, otherwise.
    """
    return MasterBond.objects.filter(segment_id=segment_id, master_syllabus__term__archived=True).exists()


def is_segment_previously_published(segment_id, master_syllabus_id):
    """
    Determines whether a segment is associated with any master syllabus that's published, excluding the one provided.
    The provided master syllabus should be the current one.

    Parameters:
    :param (int) segment_id:            The segment ID to check.
    :param (int) master_syllabus_id:    The master syllabus ID to exclude.

    Returns:
    :return (boolean)                   - Returns True if this segment was previously published. False, otherwise.
    """
    return (MasterBond.objects
            .filter(Q(segment_id=segment_id) & Q(visibility=True) & ~Q(master_syllabus_id=master_syllabus_id))
            .exists())


def replace_block(request, master_syllabus_id, segment_id, block, block_type):
    """
    Replaces a block on a segment. Handles blocks that required additional work to completely replace it.

    Parameters:
    :param (Request) request:           The request object (for session variables).
    :param (int) master_syllabus_id:    The ID of the master syllabus used to create an addendum, if necessary.
    :param (int) segment_id:            The ID of the segment on which to replace the old block with the new one.
    :param (Block) block:               The ID of old block to be replaced.
    :param (str) block_type:            The type of block to be replaced.

    Returns:
    :return (Boolean, Block)    - Returns a tuple containing a Boolean indicating True on success or False on failure
                                and the newly created block.
    """
    # First determine if there is an addendum for the current (new) block. If so, then we can go ahead and just update
    # the existing addendum.
    addendum = (Addendum.objects
                .filter(master_syllabus_id=master_syllabus_id, new_block_id=block.id, owner=request.user)
                .first())
    now = datetime.now()
    if addendum:
        addendum.datetime = now
        addendum.save()
        return None
    else:
        # No addendum exists, so continue with the replace operation and create the addendum afterward.
        old_block_id = block.id
        if block_type == 'details':
            block = DetailsBlock.objects.get(pk=block.id)
            valid, block = replace_block_details(request, segment_id, block)
        elif block_type == 'list':
            block = ListBlock.objects.get(pk=block.id)
            valid, block = replace_block_list(request, segment_id, block)
        elif block_type == 'schedule':
            block = ScheduleBlock.objects.get(pk=block.id)
            valid, block = replace_block_schedule(request, segment_id, block)
        elif block_type == 'table':
            block = TableBlock.objects.get(pk=block.id)
            valid, block = replace_block_table(request, segment_id, block)
        else:
            valid, block = replace_block_generic(request, segment_id, block)
        if valid:
            master_syllabus = MasterSyllabus.objects.get(pk=master_syllabus_id)
            printable_block = PrintableBlock.objects.get(pk=block.id)
            printable_block.effective_term = master_syllabus.term
            printable_block.save()
            if date.today() >= master_syllabus.term.start_date:
                addendum = Addendum(master_syllabus_id=master_syllabus_id, old_block_id=old_block_id,
                                    new_block_id=block.id, date_time=now, owner=request.user)
                addendum.save()
            return block
        else:
            return None


def replace_block_details(request, segment_id, block):
    """
    Replaces a details block on a segment. The old block is replaced by the new block.

    Parameters:
    :param (Request) request:           The request object (for session variables).
    :param (int) segment_id:            The ID of the segment on which to replace the old block with the new one.
    :param (DetailsBlock) block:        The old block to be replaced.

    Returns:
    :return (Boolean, Block)            - Returns a tuple containing a Boolean indicating True on success or False on
                                        failure and the newly created block.
    """
    old_block_id = block.id
    valid, new_block = replace_block_generic(request, segment_id, block)
    if valid:
        details = DetailsBlockDetail.objects.filter(details_block_id=old_block_id)
        for detail in details:
            detail.pk = None
            detail.details_block_id = new_block.id
            detail.save()
    return valid, new_block


def replace_block_generic(request, segment_id, block):
    """
    Replaces a block on a segment. The old block is replaced by the new block.

    Parameters:
    :param (Request) request:   The request object (for session variables).
    :param (int) segment_id:    The ID of the segment on which to replace the old block with the new one.
    :param (Block) block:       The old block to be replaced.

    Returns:
    :return (Boolean, Block)    - Returns a tuple containing a Boolean indicating True on success or False on failure
                                and the newly created block.
    """
    try:
        old_block_id = block.id
        block.pk = None
        block.id = None
        block.block_ptr_id = None
        block.printableblock_ptr_id = None
        block._state.adding = True
        block.save()
        old_bond = Bond.objects.get(segment_id=segment_id, block_id=old_block_id)
        new_bond = Bond(segment_id=segment_id, block_id=block.id, order=old_bond.order,
                        owner=request.user)
        new_bond.save()
        old_bond.delete()
        return True, block
    except:
        return False, None


def replace_block_list(request, segment_id, block):
    """
    Replaces a list block on a segment. The old block is replaced by the new block.

    Parameters:
    :param (Request) request:   The request object (for session variables).
    :param (int) segment_id:    The ID of the segment on which to replace the old block with the new one.
    :param (ListBlock) block:   The old block to be replaced.

    Returns:
    :return (Boolean, Block)    - Returns a tuple containing a Boolean indicating True on success or False on failure
                                and the newly created block.
    """
    old_block_id = block.id
    valid, new_block = replace_block_generic(request, segment_id, block)
    if valid:
        items = ListBlockItem.objects.filter(list_block_id=old_block_id)
        for item in items:
            item.pk = None
            item.list_block_id = new_block.id
            item.save()
    return valid, new_block


def replace_block_schedule(request, segment_id, block):
    """
    Replaces a schedule block on a segment. The old block is replaced by the new block.

    Parameters:
    :param (Request) request:       The request object (for session variables).
    :param (int) segment_id:        The ID of the segment on which to replace the old block with the new one.
    :param (ScheduleBlock) block:   The old block to be replaced.

    Returns:
    :return (Boolean, Block)        - Returns a tuple containing a Boolean indicating True on success or False on
                                    failure and the newly created block.
    """
    old_block_id = block.schedule.id
    valid, new_block = replace_block_generic(request, segment_id, block)
    if valid:
        schedule = Schedule.objects.get(pk=old_block_id)
        schedule.pk = None
        schedule.save()
        units = ScheduleUnit.objects.filter(schedule_id=old_block_id)
        for unit in units:
            old_unit_id = unit.id
            unit.pk = None
            unit.schedule = schedule
            unit.save()
            topics = ScheduleTopic.objects.filter(unit__schedule_id=old_block_id, unit_id=old_unit_id)
            for topic in topics:
                topic.pk = None
                topic.unit = unit
                topic.save()
        new_block.schedule = schedule
        new_block.save()
    return valid, new_block


def replace_block_table(request, segment_id, block):
    """
    Replaces a table block on a segment. The old block is replaced by the new block.

    Parameters:
    :param (Request) request:   The request object (for session variables).
    :param (int) segment_id:    The ID of the segment on which to replace the old block with the new one.
    :param (TableBlock) block:  The old block to be replaced.

    Returns:
    :return (Boolean, Block)    - Returns a tuple containing a Boolean indicating True on success or False on failure
                                and the newly created block.
    """
    old_block_id = block.id
    valid, new_block = replace_block_generic(request, segment_id, block)
    if valid:
        columns = TableBlockColumn.objects.filter(table_id=old_block_id)
        for column in columns:
            column.pk = None
            column.table = new_block
            column.save()
        rows = TableBlockRow.objects.filter(table_id=old_block_id)
        for row in rows:
            old_row_id = row.id
            row.pk = None
            row.table = new_block
            row.save()
            cells = TableBlockCell.objects.filter(table_row_id=old_row_id)
            for cell in cells:
                cell.pk = None
                cell.table_row = row
                cell.save()
    return valid, new_block


def replace_segment(request, master_syllabus_id, segment_id):
    """
    Replaces a segment by completing a deep copy operation of it and unlinking the original segment. This operation
    is required if the segment is archived or published (or part of a Master Syllabus that is in either state).

    Parameters:
    :param (Request) request:           The request object to retrieve user and session data.
    :param (int) master_syllabus_id:    The ID of the master syllabus affected by the replacement.
    :param (int) segment_id:            The ID of the segment to be replaced.

    Returns:
    :return (int)                       Returns the ID of the newly created segment.

    """
    master_syllabus = MasterSyllabus.objects.get(pk=master_syllabus_id)
    segment = Segment.objects.get(pk=segment_id)
    segment.pk = None
    segment._state.adding = True
    segment.effective_term = master_syllabus.term
    segment.save()
    bonds = Bond.objects.filter(segment_id=segment_id)
    for bond in bonds:
        bond.pk = None
        bond.segment = segment
        bond._state.adding = True
        bond.save()
    old_master_bond = MasterBond.objects.get(master_syllabus_id=master_syllabus_id, segment_id=segment_id)
    new_master_bond = MasterBond(master_syllabus_id=master_syllabus_id, segment_id=segment.id,
                                 order=old_master_bond.order, owner=request.user, visibility=old_master_bond.visibility)
    new_master_bond.save()
    master_bond_sections = MasterBondSection.objects.filter(master_bond=old_master_bond)
    if master_bond_sections.count() > 0:
        for master_bond_section in master_bond_sections:
            master_bond_section.pk = None
            master_bond_section.master_bond = new_master_bond
            master_bond_section._state.adding = True
            master_bond_section.save()
    old_master_bond.delete()
    return segment.id


def swap_orders(bond, other_bond):
    """
    Swaps the order attribute of two bonds or masterbonds.

    Parameters:
    :param (Bond) bond:         The first bond to swap orders.
    :param (Bond) other_bond:   The second bond to swap orders.

    Returns:
    :return (void)
    """
    other_order = other_bond.order
    other_bond.order = bond.order
    bond.order = other_order
    bond.save()
    other_bond.save()


def verify_block_course(master_syllabus, segment, block):
    """
    Ensures that a dynamic block is associated with the same course as the section assigned to its segment.

    Parameters:
    :param (MasterSyllabus) master_syllabus:        The master syllabus to verify.
    :param (Segment) segment:                       The segment to verify.
    :param (Block) block:                           The block to verify.

    Returns:
    :return (boolean)                               - Returns True if the block is considered valid, False otherwise.
    """
    master_bond = MasterBond.objects.get(master_syllabus=master_syllabus, segment=segment)
    master_bond_sections = MasterBondSection.objects.filter(master_bond=master_bond)
    if hasattr(block, 'printableblock'):
        if hasattr(block.printableblock, 'scheduleblock'):
            if master_bond_sections:
                for master_bond_section in master_bond_sections:
                    if block.printableblock.scheduleblock.schedule.course != master_bond_section.section.course:
                        return False
            else:
                if block.printableblock.scheduleblock.schedule.course:
                    return False
    return True


def verify_master_bond_course(master_bond):
    """
    Ensures that all dynamic blocks associated with a master bond have a course that matches the course associated with
    this master bond's (course) section.

    Parameters:
    :param (MasterBond) master_bond:     The master bond to verify.

    Returns:
    :return (boolean)                    - Returns True if the master bond is considered valid, False otherwise.
    """
    master_bond_valid = True
    schedule_blocks = ScheduleBlock.objects.filter(bond__segment=master_bond.segment)
    master_bond_sections = MasterBondSection.objects.filter(master_bond=master_bond)
    if master_bond_sections:
        for master_bond_section in master_bond_sections:
            for schedule_block in schedule_blocks:
                if schedule_block.schedule.course != master_bond_section.section.course:
                    master_bond_valid = False
    else:
        # There are no master bond section associations, so make sure that there are no blocks that require one.
        for schedule_block in schedule_blocks:
            if schedule_block.schedule.course:
                master_bond_valid = False
    return master_bond_valid


def verify_master_syllabus_content(master_syllabus):
    """
    Ensures that all segments within a master segment have at least one block associated with them.

    Parameters:
    :param (MasterSyllabus) master_syllabus:     The master segment to verify.

    Returns:
    :return (tuple)                              - Returns a tuple with the first value indicating whether a master
                                                 segment is vali or not. The second value consists of a list containing
                                                 invalid segments.
    """
    master_syllabus_valid = True
    invalid_segments = []
    master_bonds = MasterBond.objects.filter(master_syllabus=master_syllabus)
    for master_bond in master_bonds:
        blocks = Block.objects.filter(bond__segment=master_bond.segment).count()
        if blocks == 0:
            master_syllabus_valid = False
            invalid_segments.append(master_bond.segment.name)
    return master_syllabus_valid, invalid_segments


def verify_master_syllabus_course(master_syllabus):
    """
    Ensures that all dynamic blocks within a master segment have a course that matches the course associated with this
    master segment.

    Parameters:
    :param (MasterSyllabus) master_syllabus:    The master segment to verify.

    Returns:
    :return (tuple)                             - Returns a tuple with the first value indicating whether a master
                                                segment is valid or not. The second value consists of a list containing
                                                invalid segments.
    """
    master_syllabus_valid = True
    invalid_segments = []
    master_bonds = MasterBond.objects.filter(master_syllabus=master_syllabus)
    for master_bond in master_bonds:
        if not verify_master_bond_course(master_bond):
            master_syllabus_valid = False
            invalid_segments.append(master_bond.segment.name)
    return master_syllabus_valid, invalid_segments
