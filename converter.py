import cv2
import re
import tempfile
from fpdf import FPDF
from PIL import Image
import glob
import os
import sys
import platform
from pdf2image import convert_from_path


class Converter:
	"""
		Converts PDF Files to Image
		Inverts Image
		Reconvert to PDF and Combine
	"""

	def invert_image(self, i_input, i_output):
		"""
		:param i_input: image to be inverted
		:param i_output: output image
		"""
		image = cv2.imread(i_input)
		print('Inverting image: {}'.format(i_input))
		image = ~image
		cv2.imwrite(i_output, image)

	def pdf_to_img(self, file_path, o_dir):
		"""

		:param p_dir:  input directory
		:param o_dir:  output directory
		"""
		pdf_to_images = convert_from_path(file_path)
		for i in range(len(pdf_to_images)):
			pdf_to_images[i].save(o_dir + str(i) + '.jpeg', 'JPEG')

	def img_to_pdf(self, i_dir, o_dir, filename):
		"""
		:param i_dir: images directory
		:param o_dir: output directory
		"""
		imgtopdf = FPDF()
		images = []
		for filepath in glob.iglob(i_dir + '/*.jpeg'):
			print('Inverting the images: {}'.format(filepath))
			self.invert_image(filepath, filepath)
			images.append(filepath)

		images = [int(re.findall('\d+.jpeg', i)[0].split('.jpeg')[0]) for i in images]
		images.sort()

		for i in images:
			img = '{}'.format(i_dir+str(i)+'.jpeg')
			print('Converting images to PDF files: {}'.format(img))
			cover = Image.open(img)
			width, height = cover.size

			# convert pixel in mm with 1px=0.264583 mm
			width, height = float(width * 0.264583), float(height * 0.264583)

			# given we are working with A4 format size
			pdf_size = {'P': {'w': 210, 'h': 297}, 'L': {'w': 297, 'h': 210}}

			# get page orientation from image size
			orientation = 'P' if width < height else 'L'

			#  make sure image size is not greater than the pdf format size
			width = width if width < pdf_size[orientation]['w'] else pdf_size[orientation]['w']
			height = height if height < pdf_size[orientation]['h'] else pdf_size[orientation]['h']

			imgtopdf.add_page(orientation=orientation)

			imgtopdf.image(img, 0, 0, width, height)

		print('Generating combined PDF file {}'.format(o_dir + filename))
		imgtopdf.output(o_dir + filename, 'F')

	def clean_up(self, dir):
		"""
		:param dir:
		"""
		file_list = glob.glob(os.path.join(dir, "*.pdf"))
		for f in file_list:
			os.remove(f)


if __name__ == '__main__':
	con = Converter()
	pdf_list = [f for f in glob.glob("./ORIPDF/*.pdf")]
	if len(pdf_list)==0:
		print('There is no given PDF Files under ORIPDF, skipping operation...')
		sys.exit(0)
	for pdf in pdf_list:
		if platform.system() == "Windows":
			file_name = pdf.split('./ORIPDF\\')[1]
		else:
			file_name = pdf.split('./ORIPDF/')[1]
		temp_file = tempfile.TemporaryDirectory()
		con.pdf_to_img(pdf, temp_file.name + '/')
		con.img_to_pdf(temp_file.name + '/', './', file_name)
		os.remove(pdf)
