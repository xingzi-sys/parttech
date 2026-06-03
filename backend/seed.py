from app import create_app
from app.extensions import db
from app.models.user import User, Role, Permission
from app.models.partner import Partner
from app.models.contact import Contact
from app.models.product import Product

def seed_data():
    app = create_app()
    with app.app_context():
        db.create_all()

        if Permission.query.count() > 0:
            print('数据已存在，跳过初始化')
            return

        perms = [
            {'name': '查看企业', 'code': 'partner_view', 'description': '查看合作商信息'},
            {'name': '编辑企业', 'code': 'partner_edit', 'description': '编辑合作商信息'},
            {'name': '删除企业', 'code': 'partner_delete', 'description': '删除合作商'},
            {'name': '查看项目', 'code': 'project_view', 'description': '查看项目信息'},
            {'name': '编辑项目', 'code': 'project_edit', 'description': '编辑项目信息'},
            {'name': '查看合同', 'code': 'contract_view', 'description': '查看合同信息'},
            {'name': '编辑合同', 'code': 'contract_edit', 'description': '编辑合同信息'},
            {'name': '用户管理', 'code': 'user_manage', 'description': '管理系统用户'},
            {'name': '系统配置', 'code': 'system_config', 'description': '系统配置'},
        ]

        permissions = []
        for p in perms:
            perm = Permission(**p)
            db.session.add(perm)
            permissions.append(perm)

        roles = [
            {'name': '超级管理员', 'code': 'admin', 'description': '系统超级管理员', 'level': 100},
            {'name': '部门管理员', 'code': 'manager', 'description': '部门经理/负责人', 'level': 50},
            {'name': '项目经理', 'code': 'pm', 'description': '负责项目跟进', 'level': 20},
            {'name': '普通成员', 'code': 'member', 'description': '普通成员', 'level': 10},
        ]

        role_objects = {}
        for r in roles:
            role = Role(**r)
            db.session.add(role)
            role_objects[r['code']] = role

        role_objects['admin'].permissions = permissions
        role_objects['manager'].permissions = permissions[:8]
        role_objects['pm'].permissions = permissions[:6]
        role_objects['member'].permissions = permissions[:4]

        admin = User(
            username='admin',
            email='admin@parttech.com',
            real_name='系统管理员',
            department='技术部',
            position='管理员'
        )
        admin.set_password('admin123')
        admin.roles.append(role_objects['admin'])

        db.session.add(admin)

        demo_manager = User(
            username='manager',
            email='manager@parttech.com',
            real_name='张经理',
            department='智算业务部',
            position='部门经理'
        )
        demo_manager.set_password('manager123')
        demo_manager.roles.append(role_objects['manager'])

        db.session.add(demo_manager)

        demo_user = User(
            username='user',
            email='user@parttech.com',
            real_name='李同事',
            department='智算业务部',
            position='项目经理'
        )
        demo_user.set_password('user123')
        demo_user.roles.append(role_objects['pm'])

        db.session.add(demo_user)

        partners = [
            {'name': '智算未来科技', 'type': '智算平台', 'level': '战略', 'status': '活跃', 'tags': 'GPU集群,液冷', 'description': '领先的智算平台提供商'},
            {'name': '华新数据中心', 'type': '机房设备', 'level': '核心', 'status': '活跃', 'tags': '机房,服务器', 'description': '专业数据中心服务商'},
            {'name': '创新AI解决方案', 'type': '行业产品', 'level': '核心', 'status': '活跃', 'tags': '大模型,行业方案', 'description': 'AI行业应用专家'},
            {'name': '金桥资本', 'type': '资金方', 'level': '战略', 'status': '活跃', 'tags': '投资,垫资', 'description': '智算项目资金支持'},
            {'name': '云智科技', 'type': '整体方案', 'level': '普通', 'status': '活跃', 'tags': '信创,整体方案', 'description': '信创整体解决方案商'},
        ]

        partner_objects = []
        for p in partners:
            partner = Partner(**p)
            db.session.add(partner)
            partner_objects.append(partner)

        contacts = [
            {'partner_id': 1, 'name': '王总', 'position': 'CEO', 'role': '决策者', 'phone': '13800138001', 'email': 'wang@smartai.com', 'is_primary': True},
            {'partner_id': 1, 'name': '张经理', 'position': '商务经理', 'role': '执行者', 'phone': '13800138002', 'email': 'zhang@smartai.com'},
            {'partner_id': 2, 'name': '李总监', 'position': '运营总监', 'role': '决策者', 'phone': '13800138003', 'email': 'li@huaxin.com', 'is_primary': True},
            {'partner_id': 3, 'name': '赵工', 'position': '技术负责人', 'role': '影响者', 'phone': '13800138004', 'email': 'zhao@innovate.com'},
            {'partner_id': 4, 'name': '钱总', 'position': '投资总监', 'role': '决策者', 'phone': '13800138005', 'email': 'qian@jinqiao.com', 'is_primary': True},
        ]

        for c in contacts:
            contact = Contact(**c)
            db.session.add(contact)

        products = [
            {'partner_id': 1, 'name': '智算云平台', 'category': '平台软件', 'status': '在售', 'description': 'GPU算力租赁平台', 'scenarios': '大模型训练,推理'},
            {'partner_id': 1, 'name': 'AI训练集群', 'category': '算力资源', 'status': '在售', 'description': '千卡GPU训练集群', 'scenarios': '大模型训练'},
            {'partner_id': 2, 'name': '液冷服务器', 'category': '算力资源', 'status': '在售', 'description': '浸没式液冷服务器', 'scenarios': '数据中心'},
            {'partner_id': 3, 'name': '金融大模型', 'category': '行业应用', 'status': '在售', 'description': '金融行业垂直大模型', 'scenarios': '智能客服,风控'},
            {'partner_id': 5, 'name': '信创服务器', 'category': '配套服务', 'status': '在售', 'description': '国产化服务器', 'scenarios': '信创替代'},
        ]

        for p in products:
            product = Product(**p)
            db.session.add(product)

        db.session.commit()
        print('初始化数据成功!')
        print('默认账号: admin/admin123')

if __name__ == '__main__':
    seed_data()