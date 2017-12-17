import numpy as np
import tensorflow as tf
from config import Config
import librosa

############################################################################
##  Spectrogram util functions
############################################################################

def create_spectrogram_from_audio(data):
	global setting
	spectrogram = librosa.stft(data, n_fft=Config.n_fft, hop_length=Config.hop_length).transpose()

	# divide the real and imaginary components of each element 
	# concatenate the matrix with the real components and the matrix with imaginary components
	# (DataCorruptionError when saving complex numbers in TFRecords)
	
	# concatenated = np.concatenate([np.real(spectrogram), np.imag(spectrogram)], axis=1)
	return spectrogram # [num_time_frames, num_freq_bins]

def spectrogram_split_real_imag(spec):
	return np.concatenate([np.real(spec), np.imag(spec)], axis=1)


def create_audio_from_spectrogram(spec):
	spec_transposed = tf.transpose(spec).eval()
	return librosa.istft(spec_transposed, Config.hop_length)

def apply_mask(spec, mask):
	mag_spec = tf.abs(spec)
	phase_spec = get_phase(spec)
	print (mag_spec)
	return tf.multiply(tf.cast(tf.multiply(mag_spec, mask), tf.complex64), tf.exp(tf.complex(tf.zeros_like(mag_spec), phase_spec)))

def get_phase(spec):
	return tf.imag(tf.log(spec))

############################################################################
##  Vector Product Functions
############################################################################

def vector_product_matrix(X, W):
	# order different from paper since dimensions are transposed to make batch processing easier
	return tf.transpose([tf.matmul(X[:,:,2], W[:,:,1]) - tf.matmul(X[:,:,1], W[:,:,2]),
		tf.matmul(X[:,:,0], W[:,:,2]) - tf.matmul(X[:,:,2], W[:,:,0]),
		tf.matmul(X[:,:,1], W[:,:,0]) - tf.matmul(X[:,:,0], W[:,:,1])], (1, 2, 0))