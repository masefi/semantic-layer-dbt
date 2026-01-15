with items as (
    select distinct order_id, product_id, product_name, category 
    from {{ ref('int_order_items_enriched') }}
),

product_stats as (
    select 
        product_id, 
        count(distinct order_id) as product_order_count
    from items
    group by 1
),

total_orders as (
    select count(distinct order_id) as total_order_count from items
),

pairs as (
    select
        a.product_id as product_id_a,
        a.product_name as product_name_a,
        a.category as category_a,
        b.product_id as product_id_b,
        b.product_name as product_name_b,
        b.category as category_b,
        count(distinct a.order_id) as co_occurrence_count
    from items a
    join items b on a.order_id = b.order_id
    where a.product_id < b.product_id
    group by 1, 2, 3, 4, 5, 6
    having count(distinct a.order_id) >= 10
)

select
    p.product_id_a,
    p.product_name_a,
    p.category_a,
    p.product_id_b,
    p.product_name_b,
    p.category_b,
    p.co_occurrence_count,
    
    pa.product_order_count as product_a_order_count,
    pb.product_order_count as product_b_order_count,
    t.total_order_count,
    
    -- Support: P(A and B)
    safe_divide(p.co_occurrence_count, t.total_order_count) as support,
    
    -- Confidence: P(B|A) = P(A and B) / P(A)
    safe_divide(p.co_occurrence_count, pa.product_order_count) as confidence_a_to_b,
    
    -- Confidence: P(A|B) = P(A and B) / P(B)
    safe_divide(p.co_occurrence_count, pb.product_order_count) as confidence_b_to_a,
    
    -- Lift: P(A and B) / (P(A) * P(B))
    safe_divide(
        safe_divide(p.co_occurrence_count, t.total_order_count),
        (safe_divide(pa.product_order_count, t.total_order_count) * safe_divide(pb.product_order_count, t.total_order_count))
    ) as lift

from pairs p
join product_stats pa on p.product_id_a = pa.product_id
join product_stats pb on p.product_id_b = pb.product_id
cross join total_orders t
order by lift desc
