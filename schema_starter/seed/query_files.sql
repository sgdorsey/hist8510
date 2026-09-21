WITH andersonpv AS (
SELECT *
FROM church
WHERE county = 'Anderson'
ORDER BY church.property_value DESC)


SELECT *
FROM andersonpv
WHERE property_value IS NOT NULL
ORDER BY year_organized DESC;


SELECT name_of_church,
       denomination,
       year_organized,
       property_value
FROM church
WHERE county = 'Anderson'
  AND property_value IS NOT NULL
ORDER BY property_value DESC
LIMIT 15;


SELECT city.city_name,
       COUNT(*) AS churches,
       ROUND(AVG(church.property_value), 2) AS avg_property_value
FROM church
JOIN city ON church.city_id = city.city_id
WHERE typeof(church.property_value) IN ('integer', 'real')
GROUP BY city.city_id, city.city_name
ORDER BY avg_property_value DESC;

SELECT city.city_name,
       church.denomination,
       COUNT(*) AS churches,
       ROUND(AVG(church.property_value), 2) AS avg_property_value
FROM church
JOIN city ON church.city_id = city.city_id
WHERE typeof(church.property_value) IN ('integer', 'real')
GROUP BY city.city_id, city.city_name, church.denomination
ORDER BY city.city_name, avg_property_value DESC;