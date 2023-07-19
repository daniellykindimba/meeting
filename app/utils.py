async def paginator(data, page, page_size=25):
    """
    paginator to limit the flow of the data to render
    :param request:
    :param res:
    :return:
    """
    note_per_page = page_size
    page = int(page if page else 1)
    start = 0
    end = note_per_page
    if page > 0:
        start = note_per_page * page
        end = note_per_page * (page + 1)
    if len(data) >= end:
        payload = data[start:end]
    else:
        if page == 0:
            payload = data[0:len(data)]
        else:
            payload = data[note_per_page * (page - 1):note_per_page * page]
    return payload


async def get_paginator(qs, page, page_size, paginated_type, **kwargs):
    p = await paginator(qs, page, page_size)
    page_obj = p
    return paginated_type(
        total=len(qs),
        page=page,
        pages=int(len(qs) / page_size) + 1,
        has_next=page < int(len(qs) / page_size) + 1,
        has_prev=page > 1,
        results=page_obj,
        **kwargs
    )