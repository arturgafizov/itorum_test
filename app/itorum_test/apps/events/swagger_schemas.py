
tags_events = ['Events']
tags_subject = ['Subject']



events_list = {
    'operation_description': '## Получение списка событий отсортированных от предстоящих',
    'operation_summary': 'Получение списка событий',
    'tags': tags_events,
}

my_events_list = {
    'operation_description': '## Получение списка моих предстоящих событий',
    'operation_summary': 'Получение списка моих предстоящих событий',
    'tags': tags_events,
}

events_retrieve = {
    'operation_description': '## Получение события',
    'operation_summary': 'Получение события',
    'tags': tags_events,
}

events_destroy = {
    'operation_description': '## Удаление события',
    'operation_summary': 'Удаление события',
    'tags': tags_events,
}

update_event_status = {
    'operation_description': '## Обновление статуса события'                             
                             '```'
                             '(("pending", "Ожидается"), ("completed", "Завершено"), ("cancelled", "Отменено"))'
                             '```',
    'operation_summary': 'Обновление статуса события',
    'tags': tags_events,
}

description_search = {
    'operation_description': '## Фильтр по полю описание'              
                             '```'                             
                             'полнотекстовый поиск'
                             '```',
    'operation_summary': 'Обновление статуса события',
    'tags': tags_events,
}

book_event = {
    'operation_description': '## Забронировать событие',
    'operation_summary': 'Забронировать событие',
    'tags': tags_events,
}

cancel_book_event = {
    'operation_description': '## Отмена брони событие',
    'operation_summary': 'Отмена брони событие',
    'tags': tags_events,
}