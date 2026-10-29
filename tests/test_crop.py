import importlib.util
from pathlib import Path
import tempfile
import unittest
from PIL import Image, ImageCms

spec = importlib.util.spec_from_file_location('crop', Path(__file__).parents[1] / 'crop.py')
crop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crop)


class ColorProfileTests(unittest.TestCase):
    def test_palette_image_with_rgb_profile_is_transformed_and_tagged(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            source = folder / 'palette.png'
            profile = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
            palette = Image.new('P', (8, 8))
            palette.putpalette([255, 0, 0] + [0, 0, 0] * 255)
            palette.save(source, icc_profile=profile)
            crop.process_image(source, folder)
            with Image.open(folder / 'palette_1524x2200.png') as actual:
                self.assertIn('icc_profile', actual.info)
                self.assertEqual(actual.getpixel((0, 0)), (255, 0, 0))

    def test_lab_pixels_are_converted_before_rgb_and_output_has_srgb_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            source = folder / 'input.tif'
            out = folder / 'output'
            out.mkdir()
            lab_profile = ImageCms.ImageCmsProfile(ImageCms.createProfile('LAB')).tobytes()
            Image.new('LAB', (12, 16), (128, 160, 100)).save(source, icc_profile=lab_profile)
            crop.process_image(source, out)
            with Image.open(out / 'input_1524x2200.tif') as actual:
                self.assertEqual(actual.size, (1524, 2200))
                self.assertEqual(actual.mode, 'RGB')
                actual_profile = ImageCms.ImageCmsProfile(__import__('io').BytesIO(actual.info['icc_profile']))
                self.assertIn('sRGB', ImageCms.getProfileDescription(actual_profile))
                with Image.open(source) as original:
                    expected = ImageCms.profileToProfile(original, ImageCms.ImageCmsProfile(__import__('io').BytesIO(lab_profile)), ImageCms.createProfile('sRGB'), outputMode='RGB')
                    self.assertEqual(actual.getpixel((0, 0)), expected.getpixel((0, 0)))

    def test_untagged_image_does_not_gain_an_unverified_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            source = folder / 'input.png'
            Image.new('RGB', (10, 10), 'red').save(source)
            crop.process_image(source, folder)
            with Image.open(folder / 'input_1524x2200.png') as actual:
                self.assertNotIn('icc_profile', actual.info)

    def test_invalid_profile_is_not_inherited_after_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            source = folder / 'invalid.png'
            Image.new('RGB', (10, 10), 'blue').save(source, icc_profile=b'not a valid ICC profile')
            crop.process_image(source, folder)
            with Image.open(folder / 'invalid_1524x2200.png') as actual:
                self.assertNotIn('icc_profile', actual.info)
                self.assertEqual(actual.getpixel((0, 0)), (0, 0, 255))


if __name__ == '__main__':
    unittest.main()
