"""Test decoders."""
from __future__ import absolute_import, division, print_function

import os
import unittest

import torch

import ctcdecode


class TestDecoders(unittest.TestCase):
    def setUp(self):
        self.vocab_list = ["'", " ", "a", "b", "c", "d", "_"]
        self.beam_size = 20
        self.probs_seq1 = [
            [
                0.06390443,
                0.21124858,
                0.27323887,
                0.06870235,
                0.0361254,
                0.18184413,
                0.16493624,
            ],
            [
                0.03309247,
                0.22866108,
                0.24390638,
                0.09699597,
                0.31895462,
                0.0094893,
                0.06890021,
            ],
            [
                0.218104,
                0.19992557,
                0.18245131,
                0.08503348,
                0.14903535,
                0.08424043,
                0.08120984,
            ],
            [
                0.12094152,
                0.19162472,
                0.01473646,
                0.28045061,
                0.24246305,
                0.05206269,
                0.09772094,
            ],
            [
                0.1333387,
                0.00550838,
                0.00301669,
                0.21745861,
                0.20803985,
                0.41317442,
                0.01946335,
            ],
            [
                0.16468227,
                0.1980699,
                0.1906545,
                0.18963251,
                0.19860937,
                0.04377724,
                0.01457421,
            ],
        ]
        self.probs_seq2 = [
            [
                0.08034842,
                0.22671944,
                0.05799633,
                0.36814645,
                0.11307441,
                0.04468023,
                0.10903471,
            ],
            [
                0.09742457,
                0.12959763,
                0.09435383,
                0.21889204,
                0.15113123,
                0.10219457,
                0.20640612,
            ],
            [
                0.45033529,
                0.09091417,
                0.15333208,
                0.07939558,
                0.08649316,
                0.12298585,
                0.01654384,
            ],
            [
                0.02512238,
                0.22079203,
                0.19664364,
                0.11906379,
                0.07816055,
                0.22538587,
                0.13483174,
            ],
            [
                0.17928453,
                0.06065261,
                0.41153005,
                0.1172041,
                0.11880313,
                0.07113197,
                0.04139363,
            ],
            [
                0.15882358,
                0.1235788,
                0.23376776,
                0.20510435,
                0.00279306,
                0.05294827,
                0.22298418,
            ],
        ]
        self.greedy_result = ["ac'bdc", "b'da"]
        self.beam_search_result = ["acdc", "b'a", "a a"]

    def convert_to_string(self, tokens, vocab, seq_len):
        return "".join([vocab[x] for x in tokens[0:seq_len]])

    def test_beam_search_decoder_1(self):
        probs_seq = torch.FloatTensor([self.probs_seq1])
        decoder = ctcdecode.CTCBeamDecoder(
            self.vocab_list,
            beam_width=self.beam_size,
            blank_id=self.vocab_list.index("_"),
        )
        beam_result, beam_scores, timesteps, out_seq_len = decoder.decode(probs_seq)
        output_str = self.convert_to_string(
            beam_result[0][0], self.vocab_list, out_seq_len[0][0]
        )
        self.assertEqual(output_str, self.beam_search_result[0])

    def test_beam_search_decoder_2(self):
        probs_seq = torch.FloatTensor([self.probs_seq2])
        decoder = ctcdecode.CTCBeamDecoder(
            self.vocab_list,
            beam_width=self.beam_size,
            blank_id=self.vocab_list.index("_"),
        )
        beam_result, beam_scores, timesteps, out_seq_len = decoder.decode(probs_seq)
        output_str = self.convert_to_string(
            beam_result[0][0], self.vocab_list, out_seq_len[0][0]
        )
        self.assertEqual(output_str, self.beam_search_result[1])

    def test_beam_search_decoder_3(self):
        lm_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test.arpa")
        probs_seq = torch.FloatTensor([self.probs_seq2])

        decoder = ctcdecode.CTCBeamDecoder(
            self.vocab_list,
            beam_width=self.beam_size,
            blank_id=self.vocab_list.index("_"),
            model_path=lm_path,
        )
        beam_result, beam_scores, timesteps, out_seq_len = decoder.decode(probs_seq)
        output_str = self.convert_to_string(
            beam_result[0][0], self.vocab_list, out_seq_len[0][0]
        )
        self.assertEqual(output_str, self.beam_search_result[2])

    def test_beam_search_decoder_batch(self):
        probs_seq = torch.FloatTensor([self.probs_seq1, self.probs_seq2])
        decoder = ctcdecode.CTCBeamDecoder(
            self.vocab_list,
            beam_width=self.beam_size,
            blank_id=self.vocab_list.index("_"),
            num_processes=24,
        )
        beam_results, beam_scores, timesteps, out_seq_len = decoder.decode(probs_seq)
        output_str1 = self.convert_to_string(
            beam_results[0][0], self.vocab_list, out_seq_len[0][0]
        )
        output_str2 = self.convert_to_string(
            beam_results[1][0], self.vocab_list, out_seq_len[1][0]
        )
        self.assertEqual(output_str1, self.beam_search_result[0])
        self.assertEqual(output_str2, self.beam_search_result[1])
        del decoder

    def test_beam_search_decoder_batch_log(self):
        probs_seq = torch.FloatTensor([self.probs_seq1, self.probs_seq2]).log()
        decoder = ctcdecode.CTCBeamDecoder(
            self.vocab_list,
            beam_width=self.beam_size,
            blank_id=self.vocab_list.index("_"),
            log_probs_input=True,
            num_processes=24,
        )
        beam_results, beam_scores, timesteps, out_seq_len = decoder.decode(probs_seq)
        output_str1 = self.convert_to_string(
            beam_results[0][0], self.vocab_list, out_seq_len[0][0]
        )
        output_str2 = self.convert_to_string(
            beam_results[1][0], self.vocab_list, out_seq_len[1][0]
        )
        self.assertEqual(output_str1, self.beam_search_result[0])
        self.assertEqual(output_str2, self.beam_search_result[1])

    def test_online_decoder_decoding(self):
        lm_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test.arpa")
        decoder = ctcdecode.OnlineCTCBeamDecoder(
            self.vocab_list,
            beam_width=self.beam_size,
            blank_id=self.vocab_list.index("_"),
            log_probs_input=True,
            num_processes=24,
            model_path=lm_path,
        )
        state1 = ctcdecode.DecoderState(decoder)
        state2 = ctcdecode.DecoderState(decoder)

        probs_seq = torch.FloatTensor([self.probs_seq2, self.probs_seq2]).log()

        is_eos_s = [True for _ in range(len(probs_seq))]

        beam_results, beam_scores, timesteps, out_seq_len = decoder.decode(
            probs_seq, [state1, state2], is_eos_s
        )
        output_str1 = self.convert_to_string(
            beam_results[0][0], self.vocab_list, out_seq_len[0][0]
        )
        output_str2 = self.convert_to_string(
            beam_results[1][0], self.vocab_list, out_seq_len[1][0]
        )

        self.assertEqual(output_str1, self.beam_search_result[2])
        self.assertEqual(output_str2, self.beam_search_result[2])

    def test_online_decoder_decoding_no_lm(self):
        decoder = ctcdecode.OnlineCTCBeamDecoder(
            self.vocab_list,
            beam_width=self.beam_size,
            blank_id=self.vocab_list.index("_"),
            log_probs_input=True,
            num_processes=24,
        )
        state1 = ctcdecode.DecoderState(decoder)
        state2 = ctcdecode.DecoderState(decoder)

        probs_seq = torch.FloatTensor([self.probs_seq1, self.probs_seq2]).log()

        is_eos_s = [True for _ in range(len(probs_seq))]

        beam_results, beam_scores, timesteps, out_seq_len = decoder.decode(
            probs_seq, [state1, state2], is_eos_s
        )
        output_str1 = self.convert_to_string(
            beam_results[0][0], self.vocab_list, out_seq_len[0][0]
        )
        output_str2 = self.convert_to_string(
            beam_results[1][0], self.vocab_list, out_seq_len[1][0]
        )

        self.assertEqual(output_str1, self.beam_search_result[0])
        self.assertEqual(output_str2, self.beam_search_result[1])

    def test_online_decoder_decoding_with_two_calls(self):
        lm_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test.arpa")
        decoder = ctcdecode.OnlineCTCBeamDecoder(
            self.vocab_list,
            beam_width=self.beam_size,
            blank_id=self.vocab_list.index("_"),
            log_probs_input=True,
            num_processes=24,
            model_path=lm_path,
        )
        state1 = ctcdecode.DecoderState(decoder)

        probs_seq = torch.FloatTensor([self.probs_seq2]).log()

        beam_results, beam_scores, timesteps, out_seq_len = decoder.decode(
            probs_seq[:, :2], [state1], [False]
        )
        beam_results, beam_scores, timesteps, out_seq_len = decoder.decode(
            probs_seq[:, 2:], [state1], [True]
        )

        output_str1 = self.convert_to_string(
            beam_results[0][0], self.vocab_list, out_seq_len[0][0]
        )
        self.assertEqual(output_str1, self.beam_search_result[2])

    def test_online_decoder_decoding_with_two_calls_no_lm(self):
        decoder = ctcdecode.OnlineCTCBeamDecoder(
            self.vocab_list,
            beam_width=self.beam_size,
            blank_id=self.vocab_list.index("_"),
            log_probs_input=True,
            num_processes=24,
        )
        state1 = ctcdecode.DecoderState(decoder)
        state2 = ctcdecode.DecoderState(decoder)

        probs_seq = torch.FloatTensor([self.probs_seq1, self.probs_seq2]).log()

        beam_results, beam_scores, timesteps, out_seq_len = decoder.decode(
            probs_seq[:, :2], [state1, state2], [False, False]
        )
        beam_results, beam_scores, timesteps, out_seq_len = decoder.decode(
            probs_seq[:, 2:], [state1, state2], [True, True]
        )

        del state1, state2
        size = beam_results.shape
        output_str1 = self.convert_to_string(
            beam_results[0][0], self.vocab_list, out_seq_len[0][0]
        )
        output_str2 = self.convert_to_string(
            beam_results[1][0], self.vocab_list, out_seq_len[1][0]
        )

        self.assertEqual(output_str1, self.beam_search_result[0])
        self.assertEqual(output_str2, self.beam_search_result[1])

    def test_online_decoder_decoding_with_a_lot_calls_no_lm_check_size(self):
        decoder = ctcdecode.OnlineCTCBeamDecoder(
            self.vocab_list,
            beam_width=self.beam_size,
            blank_id=self.vocab_list.index("_"),
            log_probs_input=True,
            num_processes=24,
        )
        state1 = ctcdecode.DecoderState(decoder)

        probs_seq = torch.FloatTensor([self.probs_seq1]).log()

        for i in range(1000):
            beam_results, beam_scores, timesteps, out_seq_len = decoder.decode(
                probs_seq, [state1], [False, False]
            )

        beam_results, beam_scores, timesteps, out_seq_len = decoder.decode(
            probs_seq, [state1], [True, True]
        )

        del state1
        self.assertGreaterEqual(beam_results.shape[2], out_seq_len.max())

    def test_hotwords(self):
        SAMPLE_LABELS = [" ", "b", "g", "n", "s", "u", "y", ""]
        SAMPLE_VOCAB = {c: n for n, c in enumerate(SAMPLE_LABELS)}

        BUGS_PROBS = torch.zeros((4, len(SAMPLE_VOCAB)))
        BUGS_PROBS[0][SAMPLE_VOCAB.get("b")] = 1
        BUGS_PROBS[1][SAMPLE_VOCAB.get("u")] = 1
        BUGS_PROBS[2][SAMPLE_VOCAB.get("g")] = 1
        BUGS_PROBS[3][SAMPLE_VOCAB.get("s")] = 1

        BUNNY_PROBS = torch.zeros((6, len(SAMPLE_VOCAB)))
        BUNNY_PROBS[0][SAMPLE_VOCAB.get("b")] = 1
        BUNNY_PROBS[1][SAMPLE_VOCAB.get("u")] = 1
        BUNNY_PROBS[2][SAMPLE_VOCAB.get("n")] = 1
        BUNNY_PROBS[3][SAMPLE_VOCAB.get("")] = 1
        BUNNY_PROBS[4][SAMPLE_VOCAB.get("n")] = 1
        BUNNY_PROBS[5][SAMPLE_VOCAB.get("y")] = 1

        BLANK_PROBS = torch.zeros((1, len(SAMPLE_VOCAB)))
        BLANK_PROBS[0][SAMPLE_VOCAB.get("")] = 1
        SPACE_PROBS = torch.zeros((1, len(SAMPLE_VOCAB)))
        SPACE_PROBS[0][SAMPLE_VOCAB.get(" ")] = 1

        # make mixed version that can get fixed with LM
        TEST_PROBS = torch.vstack(
            [
                torch.vstack([BUGS_PROBS, BLANK_PROBS, BLANK_PROBS]) * 0.51
                + BUNNY_PROBS * 0.49,
                SPACE_PROBS,
                BUNNY_PROBS,
            ]
        )

        # without lm and without hotwords
        decoder = ctcdecode.CTCBeamDecoder(SAMPLE_LABELS, blank_id=7, beam_width=100)
        beam_result, _, _, out_seq_len = decoder.decode(
            torch.unsqueeze(TEST_PROBS, dim=0)
        )
        output_str = self.convert_to_string(
            beam_result[0][0], SAMPLE_LABELS, out_seq_len[0][0]
        )
        self.assertEqual(output_str, "bugs bunny")

        # without lm and with hotwords
        beam_result, _, _, out_seq_len = decoder.decode(
            torch.unsqueeze(TEST_PROBS, dim=0),
            hotwords=[["b", "u", "n", "n", "y"]],
            hotword_weight=10,
        )
        output_str = self.convert_to_string(
            beam_result[0][0], SAMPLE_LABELS, out_seq_len[0][0]
        )
        self.assertEqual(output_str, "bunny bunny")

        lm_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test.arpa")

        # with lm and with hotwords
        lm_decoder = ctcdecode.CTCBeamDecoder(
            SAMPLE_LABELS, model_path=lm_path, blank_id=7, beam_width=100
        )

        beam_result, _, _, out_seq_len = lm_decoder.decode(
            torch.unsqueeze(TEST_PROBS, dim=0),
            hotwords=[["b", "u", "n", "n", "y"]],
            hotword_weight=10,
        )
        output_str = self.convert_to_string(
            beam_result[0][0], SAMPLE_LABELS, out_seq_len[0][0]
        )
        self.assertEqual(output_str, "bunny bunny")

        TEST_PROBS = torch.vstack(
            [
                torch.vstack([BUGS_PROBS, BLANK_PROBS, BLANK_PROBS]) * 0.51
                + BUNNY_PROBS * 0.49,
                SPACE_PROBS,
                BUNNY_PROBS,
            ]
        )

        beam_result, _, _, out_seq_len = lm_decoder.decode(
            torch.unsqueeze(TEST_PROBS, dim=0),
            hotwords=[["b", "u", "g", "s"]],
            hotword_weight=10,
        )
        output_str = self.convert_to_string(
            beam_result[0][0], SAMPLE_LABELS, out_seq_len[0][0]
        )
        self.assertEqual(output_str, "bugs bunny")

        # hotword as a phrase
        beam_result, _, _, out_seq_len = decoder.decode(
            torch.unsqueeze(TEST_PROBS, dim=0),
            hotwords=[list("bunny bunny")],
            hotword_weight=10,
        )
        output_str = self.convert_to_string(
            beam_result[0][0], SAMPLE_LABELS, out_seq_len[0][0]
        )
        self.assertEqual(output_str, "bunny bunny")

    def test_hotwords_with_small_input(self):
        probs = [
            [0.1, 0.2, 0.2, 0.1],
            [0.4, 0.4, 0.1, 0.3],
            [0.2, 0.3, 0.1, 0.4],
            [0.3, 0.1, 0.6, 0.2],
        ]
        labels = ["_", "a", "b", " "]
        probs = torch.Tensor(probs)
        probs = torch.unsqueeze(probs.transpose(0, 1), dim=0)

        # without hotword
        decoder = ctcdecode.CTCBeamDecoder(labels, blank_id=0, beam_width=100)
        beam_result, _, _, out_seq_len = decoder.decode(probs)
        output_str = self.convert_to_string(
            beam_result[0][0], labels, out_seq_len[0][0]
        )
        self.assertEqual(output_str, "a b")

        # with hotword a
        beam_result, _, _, out_seq_len = decoder.decode(
            probs, hotwords=[["a"]], hotword_weight=10
        )
        output_str = self.convert_to_string(
            beam_result[0][0], labels, out_seq_len[0][0]
        )
        self.assertEqual(output_str, "a a")

        # with hotword b
        beam_result, _, _, out_seq_len = decoder.decode(
            probs, hotwords=[["b"]], hotword_weight=10
        )
        output_str = self.convert_to_string(
            beam_result[0][0], labels, out_seq_len[0][0]
        )
        self.assertEqual(output_str, "b b")

        # with hotword "b b"
        beam_result, _, _, out_seq_len = decoder.decode(
            probs, hotwords=[list("b b")], hotword_weight=10
        )
        output_str = self.convert_to_string(
            beam_result[0][0], labels, out_seq_len[0][0]
        )
        self.assertEqual(output_str, "b b")

        # test for passing hotword scorer to decoder call with hotword "b b"
        hotword_scorer = decoder.create_hotword_scorer(
            hotwords=[list("b b")], hotword_weight=10
        )
        beam_result, _, _, out_seq_len = decoder.decode(
            probs,
            hotword_scorer=hotword_scorer,
        )
        output_str = self.convert_to_string(
            beam_result[0][0], labels, out_seq_len[0][0]
        )
        decoder.delete_hotword_scorer(hotword_scorer)
        self.assertEqual(output_str, "b b")


if __name__ == "__main__":
    unittest.main()
