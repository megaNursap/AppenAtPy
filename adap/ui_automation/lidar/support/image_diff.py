from skimage.metrics import structural_similarity
import cv2


def compare_images(file1, file2):

	# load the two input images
	imageA = cv2.imread(r"%s" % file1)
	imageB = cv2.imread(r"%s" % file2)
	dim = (imageA.shape[1], imageA.shape[0])
	imageB = cv2.resize(imageB, dim)
	# convert the images to grayscale
	grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
	grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

	# compute the Structural Similarity Index (SSIM) between the two
	# images, ensuring that the difference image is returned
	(score, diff) = structural_similarity(grayA, grayB, full=True)
	# diff = (diff * 255).astype("uint8")
	print("SSIM: {}".format(score))
	return score

