# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the LICENSE file in
# the root directory of this source tree. An additional grant of patent rights
# can be found in the PATENTS file in the same directory.

from .. import FairseqOptimizer
from . import FairseqLRScheduler, register_lr_scheduler

@register_lr_scheduler('sgd_range_test')
class sgd_range_test(FairseqLRScheduler):
    """Decay the LR on a my fixed schedule."""

    def __init__(self, args, optimizer):
        super().__init__(args, optimizer)

        # set defaults
        args.warmup_updates = getattr(args, 'warmup_updates', 0) or 0

        self.lr = args.lr[0]
        if args.warmup_updates > 0:
            self.warmup_factor = 1. / args.warmup_updates
        else:
            self.warmup_factor = 1

    @staticmethod
    def add_args(parser):
        """Add arguments to the parser for this LR scheduler."""
        # fmt: off
        parser.add_argument('--force-anneal', '--fa', type=int, metavar='N',
                            help='force annealing at specified epoch')
        parser.add_argument('--lr-shrink', default=0.1, type=float, metavar='LS',
                            help='shrink factor for annealing, lr_new = (lr * lr_shrink)')
        parser.add_argument('--warmup-updates', default=0, type=int, metavar='N',
                            help='warmup the learning rate linearly for the first N updates')
        #parser.add_argument('--lr', default=0.1, type=float, metavar='LS',
                            #help='base lr')
        # fmt: on

    def get_next_lr(self, epoch):
        lrs = self.args.lr
        print('lrs is',lrs)
        if self.args.force_anneal is None or epoch < self.args.force_anneal:
            # use fixed LR schedule
            #next_lr = lrs[min(epoch, len(lrs) - 1)]
            
            if epoch==0:
                next_lr = self.lr
            else:
                next_lr = self.lr + 0.15
            print('epoch is ',epoch,'. lr is ',next_lr)
        else:
            # annneal based on lr_shrink
            next_lr = lrs[-1] * self.args.lr_shrink ** (epoch + 1 - self.args.force_anneal)
        return next_lr

    def step(self, epoch, val_loss=None):
        """Update the learning rate at the end of the given epoch."""
        super().step(epoch, val_loss)
        self.lr = self.get_next_lr(epoch)
        self.optimizer.set_lr(self.warmup_factor * self.lr)
        return self.optimizer.get_lr()

    def step_update(self, num_updates):
        """Update the learning rate after each update."""
        if self.args.warmup_updates > 0 and num_updates <= self.args.warmup_updates:
            self.warmup_factor = num_updates / float(self.args.warmup_updates)
            self.optimizer.set_lr(self.warmup_factor * self.lr)
        return self.optimizer.get_lr()