from django.db import migrations, models
from django.utils.text import slugify


def backfill_slugs(apps, schema_editor):
    MakerProject = apps.get_model("maker_projects", "MakerProject")
    for project in MakerProject.objects.filter(slug=""):
        base = slugify(project.title)
        slug = base
        n = 1
        while MakerProject.objects.filter(slug=slug).exclude(pk=project.pk).exists():
            slug = f"{base}-{n}"
            n += 1
        project.slug = slug
        project.save()


class Migration(migrations.Migration):

    dependencies = [
        ("maker_projects", "0014_makerproject_slug"),
    ]

    operations = [
        migrations.RunPython(backfill_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="makerproject",
            name="slug",
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
    ]