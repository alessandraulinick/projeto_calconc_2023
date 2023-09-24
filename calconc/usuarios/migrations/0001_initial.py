# Generated by Django 4.2.4 on 2023-09-24 12:40

from django.conf import settings
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import usuarios.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='E-mail')),
                ('fone', models.CharField(max_length=15, verbose_name='Telefone')),
                ('nome', models.CharField(max_length=255, verbose_name='Nome')),
                ('login', models.CharField(max_length=50, verbose_name='Login')),
                ('permissao', models.CharField(max_length=100, verbose_name='Permissão')),
                ('is_staff', models.BooleanField(default=True, verbose_name='Membro da equipe')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'usuarios',
            },
            managers=[
                ('objects', usuarios.models.UsuarioManager()),
            ],
        ),
        migrations.CreateModel(
            name='Agregado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=40, unique=True)),
                ('pen_6_30_mm', models.FloatField()),
                ('pen_4_80_mm', models.FloatField()),
                ('pen_2_40_mm', models.FloatField()),
                ('pen_1_20_mm', models.FloatField()),
                ('pen_600_um', models.FloatField()),
                ('pen_300_um', models.FloatField()),
                ('pen_150_um', models.FloatField()),
                ('pen_75_um', models.FloatField()),
                ('fundo', models.FloatField()),
                ('umidade', models.FloatField()),
                ('massa_especifica', models.FloatField()),
                ('is_deleted', models.BooleanField(default=False)),
                ('num_modificacao', models.IntegerField(default=0)),
                ('data_cadastro', models.DateTimeField(default=django.utils.timezone.now)),
                ('fk_usuario_id', models.IntegerField()),
            ],
            options={
                'db_table': 'agregado',
            },
        ),
        migrations.CreateModel(
            name='Fornecedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50)),
                ('cidade', models.CharField(max_length=50, null=True)),
                ('bairro', models.CharField(max_length=50, null=True)),
                ('logradouro', models.CharField(max_length=50, null=True)),
                ('CEP', models.CharField(max_length=8)),
                ('complemento', models.CharField(max_length=150, null=True)),
                ('cpf_cnpj', models.CharField(max_length=14)),
                ('fone_1', models.CharField(max_length=11)),
                ('fone_2', models.CharField(max_length=11, null=True)),
                ('ie', models.CharField(max_length=9, null=True)),
                ('observacao', models.CharField(max_length=200, null=True)),
                ('data_cadastro', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'fornecedor',
            },
        ),
        migrations.CreateModel(
            name='TipoAgregado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=40, unique=True)),
                ('data_cadastro', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'tipo_agregado',
            },
        ),
        migrations.CreateModel(
            name='Traco',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=20, unique=True)),
                ('descricao', models.CharField(max_length=250)),
                ('porcentagem_agua', models.FloatField()),
                ('data_cadastro', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'traco',
            },
        ),
        migrations.CreateModel(
            name='TracoAgregado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('porcentagem', models.FloatField()),
                ('agregado', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='usuarios.agregado')),
                ('traco', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='usuarios.traco')),
            ],
            options={
                'db_table': 'traco_agregado',
                'unique_together': {('traco', 'agregado')},
            },
        ),
        migrations.AddField(
            model_name='traco',
            name='agregados',
            field=models.ManyToManyField(blank=True, through='usuarios.TracoAgregado', to='usuarios.agregado'),
        ),
        migrations.CreateModel(
            name='CalculoTraco',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('volume', models.FloatField()),
                ('unidade_medida', models.CharField(max_length=10)),
                ('peso_final', models.FloatField()),
                ('data_hora', models.DateTimeField(default=django.utils.timezone.now)),
                ('fk_traco', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.traco')),
                ('fk_usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'calculo_traco',
            },
        ),
        migrations.CreateModel(
            name='AgregadosCalculo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=40)),
                ('tipo_agregado', models.CharField(max_length=50)),
                ('quantidade', models.FloatField()),
                ('unidade_medida', models.CharField(max_length=15)),
                ('fk_calculo_traco', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.calculotraco')),
            ],
            options={
                'db_table': 'agregados_calculo',
            },
        ),
        migrations.AddField(
            model_name='agregado',
            name='fk_fornecedor_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.fornecedor'),
        ),
        migrations.AddField(
            model_name='agregado',
            name='fk_tipo_agregado_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.tipoagregado'),
        ),
    ]
