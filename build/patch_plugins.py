#!/usr/bin/env python3
import copy
import shutil
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ORACLE_PROFILES = (
    ("oracle_thin", "Oracle - Modern (19c-26ai)", "drivers/oracle/modern", "drivers.oracle.modern", True),
    ("oracle_compat", "Oracle - Compatibility (11gR2-21c)", "drivers/oracle/compat", "drivers.oracle.compat", False),
    ("oracle_legacy", "Oracle - Legacy (9i/10g/11g, best effort)", "drivers/oracle/legacy", "drivers.oracle.legacy", False),
)

SIGNATURE_SUFFIXES = (".SF", ".RSA", ".DSA", ".EC")


def find_plugin(plugins_dir: Path, prefix: str) -> Path:
    matches = sorted(plugins_dir.glob(f"{prefix}_*.jar"))
    if not matches:
        raise SystemExit(f"plugin not found: {prefix}_*.jar")
    return matches[0]


def load_plugin_xml(jar_path: Path) -> ET.Element:
    with zipfile.ZipFile(jar_path) as zf:
        with zf.open("plugin.xml") as fh:
            return ET.fromstring(fh.read())


def write_plugin_jar(src_jar: Path, dst_jar: Path, root: ET.Element) -> None:
    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    dst_jar.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(src_jar) as src, zipfile.ZipFile(dst_jar, "w") as dst:
        for item in src.infolist():
            name = item.filename
            if name == "plugin.xml":
                dst.writestr(item, xml_bytes)
                continue
            if name.startswith("META-INF/") and name.upper().endswith(SIGNATURE_SUFFIXES):
                continue
            dst.writestr(item, src.read(item))


def local_jar_file(path: str, bundle: str) -> ET.Element:
    el = ET.Element("file")
    el.set("type", "jar")
    el.set("path", path)
    el.set("bundle", bundle)
    return el


def keep_license_files(driver: ET.Element) -> list[ET.Element]:
    kept = []
    for child in list(driver):
        if child.tag == "file" and child.get("type") == "license" and not str(child.get("path", "")).startswith("maven:"):
            if child.get("bundle", "").startswith("!"):
                child.attrib.pop("bundle", None)
            kept.append(child)
    return kept


def strip_download_files(driver: ET.Element) -> None:
    for child in list(driver):
        if child.tag != "file":
            continue
        path = child.get("path", "")
        file_type = child.get("type", "")
        if path.startswith("maven:") or file_type == "lib" or path.startswith("http"):
            driver.remove(child)


def replace_local_jars(driver: ET.Element, path: str, bundle: str) -> None:
    strip_download_files(driver)
    for child in list(driver):
        if child.tag == "file" and child.get("type") == "jar":
            driver.remove(child)
    licenses = keep_license_files(driver)
    for child in list(driver):
        if child.tag == "file" and child.get("type") == "license":
            driver.remove(child)
    for license_el in licenses:
        driver.append(license_el)
    driver.append(local_jar_file(path, bundle))


def clone_driver(template: ET.Element, driver_id: str, label: str, promoted: bool) -> ET.Element:
    driver = copy.deepcopy(template)
    driver.set("id", driver_id)
    driver.set("label", label)
    if promoted:
        driver.set("promoted", "1")
    elif "promoted" in driver.attrib:
        del driver.attrib["promoted"]
    for child in list(driver):
        if child.tag == "replace":
            driver.remove(child)
    return driver


def patch_oracle(root: ET.Element) -> None:
    drivers_el = None
    source = None
    for parent in root.iter("drivers"):
        for driver in list(parent):
            if driver.get("id") == "oracle_thin":
                source = driver
                drivers_el = parent
                break
        if source is not None:
            break
    if source is None or drivers_el is None:
        raise SystemExit("oracle_thin driver not found")

    for extra in list(drivers_el):
        if extra.tag == "driver" and extra.get("id") in {"oracle_compat", "oracle_legacy"}:
            drivers_el.remove(extra)

    insert_at = list(drivers_el).index(source) + 1
    for driver_id, label, path, bundle, promoted in ORACLE_PROFILES:
        if driver_id == "oracle_thin":
            source.set("label", label)
            replace_local_jars(source, path, bundle)
            continue
        cloned = clone_driver(source, driver_id, label, promoted)
        replace_local_jars(cloned, path, bundle)
        drivers_el.insert(insert_at, cloned)
        insert_at += 1


def patch_mssql(root: ET.Element) -> None:
    drivers_el = None
    source = None
    for parent in root.iter("drivers"):
        for driver in list(parent):
            if driver.get("id") == "microsoft":
                source = driver
                drivers_el = parent
                break
        if source is not None:
            break
    if source is None or drivers_el is None:
        raise SystemExit("microsoft driver not found")

    source.set("label", "SQL Server - Modern (Microsoft 13.6)")
    replace_local_jars(source, "drivers/mssql/new", "drivers.mssql.new")

    for extra in list(drivers_el):
        if extra.tag == "driver" and extra.get("id") == "microsoft_legacy":
            drivers_el.remove(extra)

    cloned = clone_driver(source, "microsoft_legacy", "SQL Server - Legacy (Microsoft 9.4, best effort)", False)
    replace_local_jars(cloned, "drivers/mssql/legacy", "drivers.mssql.legacy")
    drivers_el.insert(list(drivers_el).index(source) + 1, cloned)


def ensure_child(parent: ET.Element, tag: str, attrib: dict) -> None:
    for child in parent:
        if child.tag != tag:
            continue
        if all(child.get(key) == value for key, value in attrib.items()):
            return
    ET.SubElement(parent, tag, attrib)


def patch_base(root: ET.Element) -> None:
    for ext in root.findall("extension"):
        point = ext.get("point")
        if point == "org.jkiss.dbeaver.resources":
            for name in (
                "drivers/oracle/modern",
                "drivers/oracle/compat",
                "drivers/oracle/legacy",
                "drivers/mssql/legacy",
            ):
                ensure_child(ext, "resource", {"name": name})
        elif point == "org.jkiss.dbeaver.product.bundles":
            for bundle_id, label in (
                ("drivers.oracle.modern", "Oracle modern driver files"),
                ("drivers.oracle.compat", "Oracle compatibility driver files"),
                ("drivers.oracle.legacy", "Oracle legacy driver files"),
                ("drivers.mssql.legacy", "SQL Server legacy driver files"),
            ):
                ensure_child(ext, "bundle", {"id": bundle_id, "label": label})
        elif point == "io.cloudbeaver.driver":
            for driver_id in (
                "oracle:oracle_compat",
                "oracle:oracle_legacy",
                "sqlserver:microsoft_legacy",
            ):
                ensure_child(ext, "driver", {"id": driver_id})


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: patch_plugins.py PLUGINS_DIR OUTPUT_DIR")
    plugins_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    jobs = (
        ("org.jkiss.dbeaver.ext.oracle", patch_oracle),
        ("org.jkiss.dbeaver.ext.mssql", patch_mssql),
        ("io.cloudbeaver.resources.drivers.base", patch_base),
    )
    for prefix, patcher in jobs:
        src = find_plugin(plugins_dir, prefix)
        root = load_plugin_xml(src)
        patcher(root)
        write_plugin_jar(src, output_dir / src.name, root)
        print(f"patched {src.name}")


if __name__ == "__main__":
    main()
