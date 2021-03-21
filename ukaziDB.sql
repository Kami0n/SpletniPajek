

SELECT COUNT(*) FROM crawldb.page WHERE page_type_code!='FRONTIER' ;

SELECT COUNT(*) FROM crawldb.page;


SELECT * FROM crawldb.site ORDER BY id;
SELECT * FROM crawldb.page ORDER BY id;

SELECT * FROM crawldb.page WHERE page_type_code!='FRONTIER' AND page_type_code!='HTML' ORDER BY id;

SELECT * FROM crawldb.page WHERE page_type_code='FRONTIER' ORDER BY id;
SELECT * FROM crawldb.page WHERE page_type_code='NOTALOWED' ORDER BY id;
SELECT * FROM crawldb.page WHERE page_type_code='ERROR' ORDER BY id;

SELECT * FROM crawldb.page WHERE http_status_code>399 ORDER BY id;
SELECT count(*) FROM crawldb.page WHERE http_status_code>399 ;

SELECT * FROM crawldb.page WHERE url LIKE '%.zip' ORDER BY id;

/*DAJ NAZAJ V FRONTIER*/
UPDATE crawldb.page SET page_type_code = 'FRONTIER', hash='' WHERE 

SELECT * FROM crawldb.page WHERE page_type_code='DUPLICATE' order by hash

SELECT * FROM crawldb.page WHERE hash='b2699946a8e37a7afcc0750eee614c188af5a230cb659615319f589d4d039120'

SELECT hash, count(*) as NUM FROM crawldb.page GROUP BY hash HAVING count(*) > 1 ORDER BY NUM




SELECT * FROM crawldb.page_type ;

INSERT INTO crawldb.page_type (code) VALUES ('ERROR');
INSERT INTO crawldb.page_type (code) VALUES ('NOTALOWED');

SELECT * FROM crawldb.data_type ;




SELECT * FROM crawldb.data_type ;


SELECT * FROM crawldb.link ORDER BY from_page, to_page

SELECT COUNT(*) FROM crawldb.link 
