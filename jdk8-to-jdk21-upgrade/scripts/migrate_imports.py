#!/usr/bin/env python3
"""
Java源代码import语句迁移脚本
批量转换javax.*到jakarta.*
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
import json

class ImportMigrator:
    def __init__(self, src_path, dry_run=False):
        self.src_path = Path(src_path)
        self.dry_run = dry_run
        
        # 加载映射配置
        self.load_mappings()
        
        self.stats = {
            'total_files': 0,
            'modified_files': 0,
            'total_replacements': 0,
            'by_package': {}
        }
    
    def load_mappings(self):
        """加载javax到jakarta的映射"""
        self.mappings = {
            # Servlet
            'javax.servlet': 'jakarta.servlet',
            
            # Persistence (JPA)
            'javax.persistence': 'jakarta.persistence',
            
            # Bean Validation
            'javax.validation': 'jakarta.validation',
            
            # Common Annotations
            'javax.annotation': 'jakarta.annotation',
            
            # Transaction
            'javax.transaction': 'jakarta.transaction',
            
            # WebSocket
            'javax.websocket': 'jakarta.websocket',
            
            # JAX-RS
            'javax.ws.rs': 'jakarta.ws.rs',
            
            # JSON Processing
            'javax.json': 'jakarta.json',
            
            # JSON Binding
            'javax.json.bind': 'jakarta.json.bind',
            
            # XML Binding (JAXB)
            'javax.xml.bind': 'jakarta.xml.bind',
            
            # JavaMail
            'javax.mail': 'jakarta.mail',
            
            # Activation
            'javax.activation': 'jakarta.activation',
            
            # EJB
            'javax.ejb': 'jakarta.ejb',
            
            # JMS
            'javax.jms': 'jakarta.jms',
            
            # Security
            'javax.security.auth': 'jakarta.security.auth',
            'javax.security.enterprise': 'jakarta.security.enterprise',
            
            # Inject
            'javax.inject': 'jakarta.inject',
            
            # Interceptors
            'javax.interceptor': 'jakarta.interceptor',
            
            # Decorator
            'javax.decorator': 'jakarta.decorator',
            
            # Expression Language
            'javax.el': 'jakarta.el',
            
            # JSF
            'javax.faces': 'jakarta.faces',
            
            # Server Pages
            'javax.servlet.jsp': 'jakarta.servlet.jsp',
        }
    
    def migrate(self):
        """执行迁移"""
        print(f"{'[预览模式] ' if self.dry_run else ''}开始迁移: {self.src_path}")
        print("=" * 60)
        
        # 查找所有Java文件
        java_files = list(self.src_path.rglob('*.java'))
        self.stats['total_files'] = len(java_files)
        
        print(f"找到 {len(java_files)} 个Java文件")
        print()
        
        # 迁移每个文件
        for java_file in java_files:
            self.migrate_file(java_file)
        
        # 输出统计
        self.print_stats()
        
        return self.stats
    
    def migrate_file(self, file_path):
        """迁移单个Java文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            modified_content = original_content
            file_replacements = 0
            
            # 对每个映射规则进行替换
            for old_pkg, new_pkg in self.mappings.items():
                # 匹配import语句
                pattern = rf'import\s+{re.escape(old_pkg)}\.([a-zA-Z0-9_.*]+);'
                replacement = rf'import {new_pkg}.\1;'
                
                # 执行替换并统计
                new_content, count = re.subn(pattern, replacement, modified_content)
                
                if count > 0:
                    modified_content = new_content
                    file_replacements += count
                    
                    # 统计
                    if old_pkg not in self.stats['by_package']:
                        self.stats['by_package'][old_pkg] = 0
                    self.stats['by_package'][old_pkg] += count
            
            # 如果有修改
            if modified_content != original_content:
                self.stats['modified_files'] += 1
                self.stats['total_replacements'] += file_replacements
                
                relative_path = file_path.relative_to(self.src_path)
                print(f"  ✓ {relative_path} ({file_replacements}处修改)")
                
                # 写回文件（非预览模式）
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_content)
        
        except Exception as e:
            print(f"  ✗ 处理失败: {file_path} - {e}")
    
    def print_stats(self):
        """打印统计信息"""
        print("\n" + "=" * 60)
        print("迁移统计")
        print("=" * 60)
        print(f"总文件数: {self.stats['total_files']}")
        print(f"修改文件数: {self.stats['modified_files']}")
        print(f"总替换数: {self.stats['total_replacements']}")
        
        if self.stats['by_package']:
            print("\n按包统计:")
            for pkg, count in sorted(self.stats['by_package'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {pkg}: {count}处")
        
        if self.dry_run:
            print("\n⚠️  这是预览模式，未实际修改文件")
            print("   移除 --dry-run 参数执行实际迁移")
        else:
            print("\n✅ 迁移完成!")

def main():
    if len(sys.argv) < 2:
        print("用法: python migrate_imports.py <src目录路径> [--dry-run]")
        print("\n选项:")
        print("  --dry-run  预览模式，不实际修改文件")
        sys.exit(1)
    
    src_path = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    
    if not os.path.exists(src_path):
        print(f"错误: 目录不存在: {src_path}")
        sys.exit(1)
    
    migrator = ImportMigrator(src_path, dry_run=dry_run)
    
    try:
        stats = migrator.migrate()
        
        # 保存统计结果
        if not dry_run and stats['modified_files'] > 0:
            stats_file = Path(src_path).parent / 'import_migration_stats.json'
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            print(f"\n统计结果已保存: {stats_file}")
        
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
