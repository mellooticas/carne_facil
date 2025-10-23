-- Contagem de clientes por origem
SELECT created_by,
    COUNT(*) AS total
FROM core.clientes
GROUP BY created_by;
-- Total de clientes
SELECT COUNT(*) AS total_clientes
FROM core.clientes;
-- Lojas inseridas
SELECT *
FROM core.lojas;
-- Telefones por tipo
SELECT tipo,
    COUNT(*) AS total
FROM core.telefones
GROUP BY tipo;
-- CPFs duplicados
SELECT cpf,
    COUNT(*) AS qtd
FROM core.clientes
WHERE cpf IS NOT NULL
    AND cpf <> ''
GROUP BY cpf
HAVING COUNT(*) > 1;
-- Telefones sem cliente correspondente
SELECT t.*
FROM core.telefones t
    LEFT JOIN core.clientes c ON t.cliente_id = c.id
WHERE c.id IS NULL;
-- Total de telefones
SELECT COUNT(*) AS total_telefones
FROM core.telefones;