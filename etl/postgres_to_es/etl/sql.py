
FILMWORK_MODIFIED = '''
SELECT id, modified
FROM content.filmwork
WHERE modified > '{0}'
ORDER BY modified
'''

PERSON_ID_MODIFIED = '''
SELECT id, modified
FROM content.person
WHERE modified > '{0}'
ORDER BY modified
'''

PERSON_GET_FILMWORK_ID = '''
SELECT DISTINCT fw.id, fw.modified
FROM content.filmwork fw
LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
WHERE pfw.person_id IN ({0})
ORDER BY fw.modified;
'''

GENRE_ID_MODIFIED = '''
SELECT id, modified
FROM content.genre
WHERE modified > '{0}'
ORDER BY modified;
'''

GENRE_GET_FILMWORK_ID = '''
SELECT DISTINCT fw.id, fw.modified
FROM content.filmwork fw
LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
WHERE gfw.genre_id IN ({0})
ORDER BY fw.modified;
'''

FILMWORK_DATA = '''
SELECT
fw.id as fw_id,
fw.title,
fw.description,
fw.rating,
fw.type,
fw.created,
fw.modified,
pfw.role,
p.id,
p.full_name,
g.name as genre
FROM content.filmwork fw
LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
LEFT JOIN content.person p ON p.id = pfw.person_id
LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
LEFT JOIN content.genre g ON g.id = gfw.genre_id
WHERE fw.id IN ({0});
'''
