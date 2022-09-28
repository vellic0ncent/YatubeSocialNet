from django.core.paginator import Paginator


TOP_N_ENTRIES: int = 10


def form_page_obj(request, entry_instance,
                  n_entries=TOP_N_ENTRIES):
    paginator = Paginator(entry_instance, n_entries)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
