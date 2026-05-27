use  suicide_rate;


-- 1. jose luis aqui se creo la tabla principal
DROP TABLE IF EXISTS suicidios;

CREATE TABLE suicidios (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    anio SMALLINT NOT NULL,
    estado VARCHAR(50) NOT NULL,
    suicidios_hombres INT UNSIGNED NOT NULL DEFAULT 0,
    suicidios_mujeres INT UNSIGNED NOT NULL DEFAULT 0,
    suicidios_total INT UNSIGNED NOT NULL DEFAULT 0,
    poblacion BIGINT UNSIGNED NOT NULL DEFAULT 0,
    tasa_hombres DECIMAL(10,4),
    tasa_mujeres DECIMAL(10,4),
    tasa_suicidio DECIMAL(10,4),
    
    -- Índices
    INDEX idx_anio (anio),
    INDEX idx_estado (estado),
    INDEX idx_tasa_total (tasa_suicidio),
    
    -- Este es como en pycharm para evitar duplicados
    UNIQUE KEY uk_anio_estado (anio, estado)
);

-- 2. TRIGGER: Auditoría de INSERT
DROP TABLE IF EXISTS audit_log;
CREATE TABLE audit_log (
    log_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    usuario VARCHAR(50),
    accion VARCHAR(20),
    tabla VARCHAR(50),
    registro_id INT,
    datos_anteriores TEXT,
    datos_nuevos TEXT
);

-- Trigger después de INSERT
DELIMITER $$
CREATE TRIGGER trg_suicidios_insert
AFTER INSERT ON suicidios
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (usuario, accion, tabla, registro_id, datos_nuevos)
    VALUES (USER(), 'INSERT', 'suicidios', NEW.id, 
            CONCAT('anio=', NEW.anio, ', estado=', NEW.estado, 
                   ', total=', NEW.suicidios_total));
END$$

-- Trigger después de UPDATE
CREATE TRIGGER trg_suicidios_update
AFTER UPDATE ON suicidios
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (usuario, accion, tabla, registro_id, 
                           datos_anteriores, datos_nuevos)
    VALUES (USER(), 'UPDATE', 'suicidios', NEW.id,
            CONCAT('tasa_anterior=', OLD.tasa_suicidio),
            CONCAT('tasa_nueva=', NEW.tasa_suicidio));
END$$

-- Trigger después de DELETE
CREATE TRIGGER trg_suicidios_delete
AFTER DELETE ON suicidios
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (usuario, accion, tabla, registro_id, datos_anteriores)
    VALUES (USER(), 'DELETE', 'suicidios', OLD.id,
            CONCAT('anio=', OLD.anio, ', estado=', OLD.estado));
END$$

-- 3. STORED PROCEDURES

-- SP 1: Insertar o actualizar suicidios
CREATE PROCEDURE sp_upsert_suicidio(
    IN p_anio SMALLINT,
    IN p_estado VARCHAR(50),
    IN p_hombres INT,
    IN p_mujeres INT,
    IN p_total INT,
    IN p_poblacion BIGINT,
    IN p_tasa_hombres DECIMAL(10,4),
    IN p_tasa_mujeres DECIMAL(10,4),
    IN p_tasa_total DECIMAL(10,4)
)
BEGIN
    INSERT INTO suicidios (anio, estado, suicidios_hombres, suicidios_mujeres, 
                           suicidios_total, poblacion, tasa_hombres, tasa_mujeres, tasa_suicidio)
    VALUES (p_anio, p_estado, p_hombres, p_mujeres, p_total, p_poblacion, 
            p_tasa_hombres, p_tasa_mujeres, p_tasa_total)
    ON DUPLICATE KEY UPDATE
        suicidios_hombres = VALUES(suicidios_hombres),
        suicidios_mujeres = VALUES(suicidios_mujeres),
        suicidios_total = VALUES(suicidios_total),
        poblacion = VALUES(poblacion),
        tasa_hombres = VALUES(tasa_hombres),
        tasa_mujeres = VALUES(tasa_mujeres),
        tasa_suicidio = VALUES(tasa_suicidio);
END$$

-- SP 2: Obtener top 5 tasas por año
CREATE PROCEDURE sp_top5_por_anio(IN p_anio SMALLINT)
BEGIN
    SELECT estado, tasa_suicidio, suicidios_total
    FROM suicidios
    WHERE anio = p_anio AND estado != 'NACIONAL'
    ORDER BY tasa_suicidio DESC
    LIMIT 5;
END$$

-- SP 3: Evolución nacional
CREATE PROCEDURE sp_evolucion_nacional()
BEGIN
    SELECT anio, tasa_suicidio, suicidios_total, poblacion
    FROM suicidios
    WHERE estado = 'NACIONAL'
    ORDER BY anio;
END$$

-- SP 4: Comparativa por estado
CREATE PROCEDURE sp_comparativa_estado(IN p_estado VARCHAR(50))
BEGIN
    SELECT anio, tasa_suicidio, tasa_hombres, tasa_mujeres
    FROM suicidios
    WHERE estado = p_estado
    ORDER BY anio;
END$$

-- 4. VIEWS

-- Vista 1: Resumen nacional por año
CREATE OR REPLACE VIEW vw_resumen_nacional AS
SELECT anio, tasa_suicidio, suicidios_total, poblacion
FROM suicidios
WHERE estado = 'NACIONAL'
ORDER BY anio;

-- Vista 2: Top 10 tasas históricas
CREATE OR REPLACE VIEW vw_top10_historicas AS
SELECT anio, estado, tasa_suicidio, suicidios_total
FROM suicidios
WHERE estado != 'NACIONAL'
ORDER BY tasa_suicidio DESC
LIMIT 10;

-- Vista 3: Promedio por estado (2010-2024)
CREATE OR REPLACE VIEW vw_promedio_estado AS
SELECT estado, 
       ROUND(AVG(tasa_suicidio), 2) AS tasa_promedio,
       ROUND(AVG(tasa_hombres), 2) AS hombres_promedio,
       ROUND(AVG(tasa_mujeres), 2) AS mujeres_promedio,
       SUM(suicidios_total) AS total_suicidios
FROM suicidios
WHERE estado != 'NACIONAL'
GROUP BY estado
ORDER BY tasa_promedio DESC;

-- Vista 4: Brecha de género nacional
CREATE OR REPLACE VIEW vw_brecha_genero AS
SELECT anio,
       ROUND(tasa_hombres, 2) AS hombres,
       ROUND(tasa_mujeres, 2) AS mujeres,
       ROUND(tasa_hombres - tasa_mujeres, 2) AS diferencia
FROM suicidios
WHERE estado = 'NACIONAL'
ORDER BY anio;

DELIMITER ;

-- 5. MOSTRAR ESTRUCTURA CREADA
SHOW TABLES;
SHOW TRIGGERS;
SHOW PROCEDURE STATUS WHERE Db = 'suicide_rate';
SHOW FULL TABLES WHERE Table_type = 'VIEW';


-- 1. Ver los datos
SELECT * FROM suicidios LIMIT 10;

-- 2. Probar un Stored Procedure
CALL sp_top5_por_anio(2024);

-- 3. Probar otra SP
CALL sp_evolucion_nacional();

-- 4. Ver una vista
SELECT * FROM vw_top10_historicas;

-- 5. Ver otra vista
SELECT * FROM vw_resumen_nacional;

-- 6. Ver la auditoría (debe estar vacía porque no hemos hecho updates)
SELECT * FROM auditoria;

