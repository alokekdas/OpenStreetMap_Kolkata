#select key, count(*) as cnt from nodes_tags group by key order by cnt desc limit 20;
#select key, count(*) as cnt from ways_tags group by key order by cnt desc limit 20;
#select tags.value, count(*) as cnt from 
#     (select * from nodes_tags  union all
#       select * from ways_tags) tags
#where tags.key='amenity' group by tags.value order by cnt desc;

#select T1.value from
 #          (ways_tags as T0 left join ways_tags as T1) where 
#                         T0.id = T1.id and 
#                          T0.key='amenity' and T0.value='hospital' and
#                          T1.key='name';

#select count (*) from (select distinct(value) from (select * from nodes_tags union all select * #from ways_tags) where key = 'postcode');

#select value, count (*) as cnt from 
#         (select value from 
#                 (select * from nodes_tags union all select * from ways_tags) 
#           where key = 'postcode') 
#group by value order by cnt desc limit 10;

#select T1.value from 
 #         (select * from nodes_tags union all select * from ways_tags)  as T0 left join
  #         (select * from nodes_tags union all select * from ways_tags) as T1 
 #        where 
 #                     T0.id = T1.id and 
 #                      T0.key='amenity' and T0.value='university' and
  #                        T1.key='name';

#select T1.value from 
#         (select * from nodes_tags union all select * from ways_tags)  as T0 left join
#          (select * from nodes_tags union all select * from ways_tags) as T1 
#          where 
#                        T0.id = T1.id and 
#                         T0.key='amenity' and T0.value='hospital' and
#                         T1.key='name';


#select T1.value, T2.value from 
#          (select * from nodes_tags union all select * from ways_tags)  as T0 left join
#           (select * from nodes_tags union all select * from ways_tags) as T1 left join
#          (select * from nodes_tags union all select * from ways_tags) as T2
 #        where 
#                      T0.id = T1.id and T1.id = T2.id and
#                      T0.key='amenity' and T0.value='place_of_worship' and
#                      T1.key='religion' and T2.key='name' and T1.value = 'christian';

select tags.value, count (*) as cnt from 
      (select * from nodes_tags union all
       select * from ways_tags) tags
where tags.key='city' group by tags.value order by cnt desc;

